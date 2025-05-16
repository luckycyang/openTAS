import asyncio
from functools import partialmethod
from pathlib import Path
from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtQml import QmlElement
import aiohttp
import time

from .utils import remove_file_url_prefix, get_log_file_path
from ..chattts import TTSClient, TTSRequest

QML_IMPORT_NAME = "bridge.tts"
QML_IMPORT_MAJOR_VERSION = 1

class TtsHandler(QObject):
    client: TTSClient

    finished: Signal = Signal(list)

    def __init__(self, server: str):
        super().__init__()
        self.client = TTSClient(server)

    def _run(self, req: TTSRequest):
        response = asyncio.run(self.client.convert_text_to_speech(req))

        audio_list = []
        if response.code == 0 and response.audio_files:
            for audio in response.audio_files:
                audio_list.append({
                    "filename": audio.filename,
                    "url": audio.url,
                })

        self.finished.emit(audio_list)

    @Slot(TTSRequest)
    def run(self, req: TTSRequest):
        self._run(req)

    @Slot(str, str)
    def download(self, url: str, file_path: str):
        asyncio.run(_download(url, file_path))

@QmlElement
class TtsBridge(QObject):
    handler: TtsHandler
    handler_thread: QThread

    received: Signal = Signal(list)
    started: Signal = Signal(TTSRequest)
    startDownloading: Signal = Signal(str, str)

    taskFinished: Signal = Signal(str)

    @Slot(str, dict)
    def start(self, server: str, req: dict):
        request = _prepare_request(req)

        if hasattr(self, 'handler') and self.handler.client.base_url != server:
            self._change_server(server)

        if not hasattr(self, 'handler'):
            self.handler = TtsHandler(server)
            self.handler_thread = QThread()
            self.handler.moveToThread(self.handler_thread)

            self.started.connect(self.handler.run)
            # self.handler.finished.connect(self.received)
            self.handler.finished.connect(lambda audio_list: (
                self.received.emit(audio_list),
                self.taskFinished.emit("TTS Task finished at {}".format(time.strftime("%Y-%m-%d %H:%M:%S"))),
                self._write_log("TTS Task finished")
            ))
            self.startDownloading.connect(self.handler.download)

        self.handler_thread.start()
        self.started.emit(request)

    def _write_log(self, message: str):
        log_path = get_log_file_path()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")

    @Slot(str, result=str)
    def import_text(self, file_url: str) -> str:
        file_path = remove_file_url_prefix(file_url)

        text = None
        with open(file_path) as file:
            text = file.read()

        return text

    @Slot(str, str)
    def export(self, url: str, file_url: str):
        file_path = remove_file_url_prefix(file_url)
        print(f'export {url} to {file_url}')

        self.startDownloading.emit(url, file_path)

    def _change_server(self, server: str):
        self.handler.deleteLater()
        self.handler = TtsHandler(server)
        self.handler.moveToThread(self.handler_thread)

        self.started.connect(self.handler.run)
        self.handler.finished.connect(self.received)

def _prepare_request(req: dict) -> TTSRequest:
    print(req)
    return (TTSClient.Builder()
        .set_text(req['text'])
        .set_prompt(req['prompt'])
        .set_voice(req['voice'])
        .set_speed(req['speed'])
        .set_temperature(req['temperature'])
        .set_top_p(req['top_p'])
        .set_top_k(req['top_k'])
        .set_refine_max_new_token(req['refine_token'])
        .set_infer_max_new_token(req['infer_token'])
        .set_text_seed(req['seed'])
        .set_skip_refine(req['skip_refine'])
        .set_custom_voice(req['custom_voice'])
        .build())

async def _download(url: str, file_path: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                path = Path(file_path)
                path.write_bytes(await response.read())
