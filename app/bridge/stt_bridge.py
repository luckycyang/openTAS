from typing import Dict, List
from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtQml import QmlElement
import pyaudio

from funasr import FunASR, Setting

QML_IMPORT_NAME = "bridge.stt"
QML_IMPORT_MAJOR_VERSION = 1

FORMAT_MAPPING = {
    'Int8': pyaudio.paInt8,
    'Int16': pyaudio.paInt16,
    'Int24': pyaudio.paInt24,
    'Int32': pyaudio.paInt32,
    'Float32': pyaudio.paFloat32,
    'UInt8': pyaudio.paUInt8
}

class SentenceReceiver(QObject):
    new_arrived: Signal = Signal(str)
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
                self.new_arrived.emit(sentence.text)

        self.finished.emit()

    def stop(self) -> None:
        self.service.stop()

@QmlElement
class SttBridge(QObject):
    data_receiver: SentenceReceiver
    receiver_thread: QThread

    received: Signal = Signal(str)
    serviceStopped: Signal = Signal()
    
    @Slot(dict)
    def start(self, args: dict) -> None:
        setting = _prepare_setting(args)
        asr = FunASR(setting, args['server_address'])

        self.receiver_thread = QThread()
        self.data_receiver = SentenceReceiver(
            asr, args['device_index'], args['timeout']
        )
        self.data_receiver.moveToThread(self.receiver_thread)

        self.data_receiver.new_arrived.connect(self.send_sentence)
        self.receiver_thread.started.connect(self.data_receiver.run)
        self.data_receiver.finished.connect(self._stop)

        self.receiver_thread.start()

    @Slot(str)
    def send_sentence(self, s: str) -> None:
        self.received.emit(s)

    def _stop(self) -> None:
        if self.receiver_thread:
            self.data_receiver.stop()
            self.receiver_thread.quit()
            self.receiver_thread.wait()
            self.serviceStopped.emit()

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

    @Slot(str, str)
    def save_output(self, file_url: str, output: str) -> None:
        prefix = 'file://'
        if file_url.startswith(prefix):
            file_url = file_url.removeprefix(prefix)

        with open(file_url, 'w') as file:
            file.write(output)

def _parse_hot_words(s: str) -> Dict[str, int]:
    ret = {}
    
    for s in s.splitlines():
        k, v = s.split()
        ret.update({ k: int(v) })

    return ret

def _parse_chunk_size(s: str) -> List[int]:
    return [int(s) for s in s.split(',')]

def _prepare_setting(args: dict) -> Setting:
    args['audio_format'] = FORMAT_MAPPING[args['audio_format']]
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
