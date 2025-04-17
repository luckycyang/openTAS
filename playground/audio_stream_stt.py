import asyncio
import pyaudio


def microphone_lists():
    p = pyaudio.PyAudio()
    device_count = p.get_device_count()
    microphones = []

    for i in range(device_count):
        device_info = p.get_device_info_by_index(i)

        if device_info['maxInputChannels'] > 0:
            microphones.append(device_info)

    for index, info in enumerate(microphones):
        print(index, info)



if __name__ == "__main__":
    microphone_lists()
