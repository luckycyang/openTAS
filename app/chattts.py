import asyncio
import aiohttp
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class TTSRequest:
    text: str
    prompt: str = "[break_6]"
    voice: str = "11.pt"
    speed: int = 5
    temperature: float = 0.1
    top_p: float = 0.701
    top_k: int = 20
    refine_max_new_token: int = 384
    infer_max_new_token: int = 2048
    text_seed: int = 42
    skip_refine: int = 1
    custom_voice: int = 0

@dataclass
class AudioFile:
    filename: str
    url: str

@dataclass
class TTSResponse:
    code: int
    msg: str
    audio_files: Optional[List[AudioFile]] = None

class TTSClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def convert_text_to_speech(self, request: TTSRequest) -> TTSResponse:
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{self.base_url}/tts', data=request.__dict__) as response:
                response_data = await response.json()
                return self._parse_response(response_data)

    def _parse_response(self, data) -> TTSResponse:
        audio_files = [
            AudioFile(filename=audio['filename'], url=audio['url'])
            for audio in data.get('audio_files', [])
        ]
        return TTSResponse(code=data['code'], msg=data['msg'], audio_files=audio_files)

    class Builder:
        def __init__(self):
            self.request = TTSRequest(text="")

        def set_text(self, text: str):
            self.request.text = text
            return self

        def set_prompt(self, prompt: str):
            self.request.prompt = prompt
            return self

        def set_voice(self, voice: str):
            self.request.voice = voice
            return self

        def set_speed(self, speed: int):
            self.request.speed = speed
            return self

        def set_temperature(self, temperature: float):
            self.request.temperature = temperature
            return self

        def set_top_p(self, top_p: float):
            self.request.top_p = top_p
            return self

        def set_top_k(self, top_k: int):
            self.request.top_k = top_k
            return self

        def set_refine_max_new_token(self, refine_max_new_token: int):
            self.request.refine_max_new_token = refine_max_new_token
            return self

        def set_infer_max_new_token(self, infer_max_new_token: int):
            self.request.infer_max_new_token = infer_max_new_token
            return self

        def set_text_seed(self, text_seed: int):
            self.request.text_seed = text_seed
            return self

        def set_skip_refine(self, skip_refine: int):
            self.request.skip_refine = skip_refine
            return self

        def set_custom_voice(self, custom_voice: int):
            self.request.custom_voice = custom_voice
            return self

        def build(self) -> TTSRequest:
            return self.request

async def main():
    tts_client = TTSClient('http://10.70.140.111:9966')
    
    # 使用 Builder 构建请求
    request = (TTSClient.Builder()
               .set_text("我是傻逼")
               .set_voice("11.pt")
               .set_speed(5)
               .set_temperature(0.1)
               .set_top_p(0.701)
               .set_top_k(20)
               .build())
    
    response = await tts_client.convert_text_to_speech(request)
    
    if response.code == 0:
        print("Success:", response.msg)
        for audio in response.audio_files:
            print(f"Filename: {audio.filename}, URL: {audio.url}")
    else:
        print("Error:", response.msg)

if __name__ == "__main__":
    asyncio.run(main())
