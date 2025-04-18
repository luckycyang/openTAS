import websockets
import asyncio
import json
import pyaudio
import ssl
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple, Deque
from collections import deque
import threading
from queue import Queue

# @TODO C-c can stop thread, i must use kill to stop it

@dataclass
class Sentence:
    start: int  # 开始时间(ms)
    end: int    # 结束时间(ms)
    text: str   # 文本内容
    punc: str   # 标点符号
    mode: str   # 识别模式

@dataclass
class Setting:
    # 音频参数
    format: int = pyaudio.paInt16
    channels: int = 1
    rate: int = 16000
    
    # 流模型参数
    chunk_size: list = None  # [回看, 音频, 右看] * 60ms
    chunk_interval: int = 10  # chunk发送间隔
    
    # 热词
    hotwords: Dict[str, int] = None
    itn: bool = True  # 逆文本转换
    mode: str = "2pass"  # 识别模式
    ssl_enable: bool = False  # 是否启用SSL
    
    def __post_init__(self):
        if self.chunk_size is None:
            self.chunk_size = [0, 10, 5]
        
        chunk_duration = 60 * self.chunk_size[1] / self.chunk_interval
        self.samples_per_chunk = int(self.rate / 1000 * chunk_duration)
        
        if self.hotwords is None:
            self.hotwords = {}

class Recorder:
    def __init__(self, setting: Setting):
        self.setting = setting
        self.audio = pyaudio.PyAudio()
        self.stream = None
    

    def list_input_devices(self):
        print("Available input devices:")
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:  # Only show input devices
                print(f"Index: {i}, Name: {info['name']}")

    def open_stream(self, device_index: int):
        self.stream = self.audio.open(
            rate=self.setting.rate,
            channels=self.setting.channels,
            format=self.setting.format,
            input=True,
            frames_per_buffer=self.setting.samples_per_chunk,
            input_device_index=device_index
        )
    
    def read_chunk(self):
        return self.stream.read(self.setting.samples_per_chunk)
    
    def close(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()

class FunASR:
    def __init__(self, setting: Setting, uri: str = "ws://localhost:10095"):
        self.setting = setting
        self.uri = uri
        self.websocket = None
        self.recorder = None
        
        # 句子存储
        self.sentence_queue = Queue()  # 线程安全的句子队列
        self.buffer_text: str = ""
        self.last_mode: str = ""
        
        # 控制线程
        self._running = False
        self._thread = None
    
    async def _connect(self):
        ssl_context = None
        if self.setting.ssl_enable:
            ssl_context = ssl.SSLContext()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        
        protocol = "wss" if self.setting.ssl_enable else "ws"
        if not self.uri.startswith(("ws://", "wss://")):
            self.uri = f"{protocol}://{self.uri}"
        
        self.websocket = await websockets.connect(
            self.uri, 
            subprotocols=["binary"], 
            ping_interval=None, 
            ssl=ssl_context
        )
        
        init_message = json.dumps({
            "mode": self.setting.mode,
            "chunk_size": self.setting.chunk_size,
            "chunk_interval": self.setting.chunk_interval,
            "wav_name": "microphone",
            "is_speaking": True,
            "hotwords": json.dumps(self.setting.hotwords),
            "itn": self.setting.itn,
        })
        await self.websocket.send(init_message)
    
    async def _record_and_send(self):
        while self._running:
            data = self.recorder.read_chunk()
            await self.websocket.send(data)
            await asyncio.sleep(0.005)
    
    def _process_message(self, message: str):
        try:
            data = json.loads(message)
            mode = data.get("mode", "")
            text = data.get("text", "")
            
            if mode:
                self.last_mode = mode
            
            if "timestamp" in data and data["timestamp"]:
                self.buffer_text = ""
                
                if "stamp_sents" in data and data["stamp_sents"]:
                    for sent in data["stamp_sents"]:
                        sentence = Sentence(
                            start=sent.get("start", -1),
                            end=sent.get("end", -1),
                            text=sent.get("text_seg", ""),
                            punc=sent.get("punc", ""),
                            mode=self.last_mode
                        )
                        self.sentence_queue.put(sentence)
            else:
                self.buffer_text = text
            
        except json.JSONDecodeError:
            pass
    
    async def _receive_messages(self):
        while self._running:
            message = await self.websocket.recv()
            self._process_message(message)
    
    async def _run_async(self, device_index: int):
        try:
            self.recorder = Recorder(self.setting)
            self.recorder.open_stream(device_index)
            await self._connect()
            
            record_task = asyncio.create_task(self._record_and_send())
            message_task = asyncio.create_task(self._receive_messages())
            
            await asyncio.gather(record_task, message_task)
        except Exception as e:
            print(f"Error in FunASR: {e}")
        finally:
            if self.recorder:
                self.recorder.close()
            if self.websocket:
                await self.websocket.close()
    
    def _run_thread(self, device_index: int):
        asyncio.run(self._run_async(device_index))
    
    def start(self, device_index: int):
        """启动识别线程"""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(
            target=self._run_thread,
            args=(device_index,),
            daemon=True
        )
        self._thread.start()
    
    def stop(self):
        """停止识别"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)
    
    def get_sentence(self, timeout: float = None) -> Optional[Sentence]:
        """
        获取一个完整句子
        :param timeout: 超时时间(秒)，None表示阻塞直到获取句子
        :return: Sentence对象或None(超时)
        """
        try:
            return self.sentence_queue.get(timeout=timeout)
        except:
            return None
    
    def get_buffer_text(self) -> str:
        """获取当前缓冲区文本（未完成的识别结果）"""
        return self.buffer_text
    
    def is_running(self) -> bool:
        """是否正在运行"""
        return self._running

# 测试用例
def test_funasr():
    setting = Setting(
        hotwords={"阿里巴巴": 20},
        ssl_enable=False
    )
    
    recorder = Recorder(setting)
    recorder.list_input_devices()


    device_index = int(input("请输入输入设备索引: "))
    funasr = FunASR(setting, uri="ws://localhost:10095")
    funasr.start(device_index)
    
    
    try:
        while True:
            sentence = funasr.get_sentence(timeout=1)
            if sentence:
                print(f"[{sentence.mode}] {sentence.text}{sentence.punc} ({sentence.start}-{sentence.end}ms)")
            
            # 显示临时结果
            buffer_text = funasr.get_buffer_text()
            if buffer_text:
                print(f"识别中: {buffer_text}", end='\r')
    except KeyboardInterrupt:
        pass
    finally:
        funasr.stop()
# TEST
def test_one():
    setting = Setting(
        
    )
    funasr = FunASR(setting)
    funasr.start(22)

# 获取结果
    while True:
        sentence = funasr.get_sentence()
        if sentence:
            # 处理完整句子
            print(f"Got sentence: {sentence.text}")
        
        # 获取临时结果（可选）
        buffer = funasr.get_buffer_text()
        
# 停止时
    funasr.stop()

if __name__ == '__main__':
    test_funasr()
    # test_one()
