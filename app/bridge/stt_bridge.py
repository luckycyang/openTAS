from typing import Dict, List, Optional
from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtQml import QmlElement
import pyaudio
import time

from ..srt_gen import SRTGenerator
from .utils import remove_file_url_prefix, get_log_file_path
from ..funasr import FunASR, Sentence, Setting

QML_IMPORT_NAME = "bridge.stt"
QML_IMPORT_MAJOR_VERSION = 1

AUDIO_FORMAT_MAPPING = {
    0: pyaudio.paInt8,
    1: pyaudio.paInt16,
    2: pyaudio.paInt24,
    3: pyaudio.paInt32,
    4: pyaudio.paFloat32,
    5: pyaudio.paUInt8
}

class SentenceReceiver(QObject):
    new_arrived: Signal = Signal(Sentence)
    finished: Signal = Signal()

    service: FunASR
    device_index: int
    timeout: float

    def __init__(self, asr: FunASR, device_index: int, timeout: float) -> None:
        super().__init__()
        self.service = asr
        self.device_index = device_index
        self.timeout = timeout

    def run(self) -> None:
        self.service.start(self.device_index)
        while self.service.is_running():
            sentence = self.service.get_sentence(self.timeout)

            if sentence:
                self.new_arrived.emit(sentence)

        self.finished.emit()

    @Slot()
    def stop(self) -> None:
        self.service.stop()

@QmlElement
class SttBridge(QObject):
    receiver: SentenceReceiver
    receiver_thread: Optional[QThread] = None
    srt_generator: Optional[SRTGenerator] = None
    output: str = ""

    received: Signal = Signal(str)
    serviceStopped: Signal = Signal()
    startingNewTask: Signal = Signal()
    finished: Signal = Signal()

    taskFinished: Signal = Signal(str)

    @Slot(dict)
    def start(self, args: dict) -> None:
        if self.receiver_thread and self.receiver_thread.isRunning():
            self.serviceStopped.emit()
            return
        
        self.output = ""
        self.startingNewTask.emit()
        if args['srt']:
            self.srt_generator = SRTGenerator()
        
        setting = _prepare_setting(args)
        asr = FunASR(setting, args['server_address'])

        self.receiver_thread = QThread()
        self.receiver = SentenceReceiver(
            asr, args['device_index'], args['timeout']
        )
        self.receiver.moveToThread(self.receiver_thread)

        self.receiver.new_arrived.connect(self.store_and_send_sentence)
        self.receiver_thread.started.connect(self.receiver.run)
        self.finished.connect(self.receiver.stop)

        self.receiver_thread.start()

    def store_and_send_sentence(self, s: Sentence) -> None:
        to_be_sent = s.text + s.punc

        if self.srt_generator:
            self.srt_generator.add(s.start, s.end, s.text)
        else:
            self.output += to_be_sent
        
        self.received.emit(to_be_sent)

    def _stop(self) -> None:
        if self.receiver_thread:
            self.finished.emit()
            self.receiver_thread.quit()
            self.serviceStopped.emit()
            self.receiver.stop()
            
            # 构造日志消息
            log_message = f"[STT] Task finished \n"
            if self.output:
                log_message += f"Transcribed text:\n{self.output}"  # 添加转换文本
            if self.srt_generator:  # 新增SRT模式日志
                log_message += f"生成字幕段数:\n{len(self.srt_generator.subtitles)}"
            
            self.taskFinished.emit(log_message)
            self._write_log(log_message)  # 写入完整日志

    def _write_log(self, message: str):
        log_path = get_log_file_path()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")

    @Slot()
    def stop(self) -> None:
        self._stop()

    @Slot(result=list)
    def send_microphone_infos(self) -> List[Dict]:
        audio = pyaudio.PyAudio()
        microphone_infos = []
        
        for i in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(i)
            if int(info['maxInputChannels']) > 0:
                microphone_infos.append({
                    'device_index': i,
                    'name': info['name'],
                })

        return microphone_infos

    @Slot(str)
    def save_output(self, file_url: str) -> None:
        file_path = remove_file_url_prefix(file_url)

        if self.srt_generator:
            self.srt_generator.save(file_path)
        else:
            with open(file_path, 'w') as file:
                file.write(self.output)

def _parse_hot_words(s: str) -> Dict[str, int]:
    ret = {}
    
    for s in s.splitlines():
        k, v = s.split()
        ret.update({ k: int(v) })

    return ret

def _parse_chunk_size(s: str) -> List[int]:
    return [int(s) for s in s.split(',')]

def _prepare_setting(args: dict) -> Setting:
    args['audio_format'] = AUDIO_FORMAT_MAPPING[args['audio_format']]
    args['hot_words'] = _parse_hot_words(args['hot_words'])
    args['chunk_size'] = _parse_chunk_size(args['chunk_size'])

    setting = Setting(
        args['audio_format'],
        args['channels'],
        args['rate'],
        args['chunk_size'],
        args['chunk_interval'],
        args['hot_words'],
        args['itn_enable'],
        args['asr_mode'],
        args['ssl_enable']
    )

    return setting
