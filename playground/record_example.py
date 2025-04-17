
import pyaudio
import wave

# Function to list available audio input devices
def list_input_devices():
    audio = pyaudio.PyAudio()
    print("Available input devices:")
    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:  # Only show input devices
            print(f"Index: {i}, Name: {info['name']}")
    audio.terminate()

# Function to record audio from a selected microphone
def record_audio(device_index, record_seconds=5, output_filename="output.wav"):
    FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
    CHANNELS = 2              # Number of audio channels (1 for mono, 2 for stereo)
    RATE = 44100              # Sample rate (samples per second)
    CHUNK = 1024              # Buffer size

    # Initialize PyAudio
    audio = pyaudio.PyAudio()

    # Start recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK,
                        input_device_index=device_index)

    print("Recording...")

    frames = []

    for _ in range(0, int(RATE / CHUNK * record_seconds)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording.")

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the recorded data as a WAV file
    with wave.open(output_filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    print(f"Audio saved to {output_filename}")

# List available input devices
list_input_devices()

# Ask the user to select a microphone
device_index = int(input("Select the microphone index: "))

# Record audio from the selected microphone
record_audio(device_index)

