class SRTGenerator:
    def __init__(self):
        self.subtitles = []
        self.index = 1

    def add(self, start_time_ms, end_time_ms, text):
        start_time = self._convert_ms_to_srt_time(start_time_ms)
        end_time = self._convert_ms_to_srt_time(end_time_ms)
        self.subtitles.append((self.index, start_time, end_time, text))
        self.index += 1

    def save(self, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            for index, start_time, end_time, text in self.subtitles:
                f.write(f"{index}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")

    def _convert_ms_to_srt_time(self, ms):
        hours = ms // 3600000
        minutes = (ms % 3600000) // 60000
        seconds = (ms % 60000) // 1000
        milliseconds = ms % 1000
        return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

# 示例用法
if __name__ == "__main__":
    srt_gen = SRTGenerator()
    srt_gen.add(1000, 5000, "Hello, world!")
    srt_gen.add(6000, 10000, "This is a subtitle generator.")
    srt_gen.save("output.srt")
