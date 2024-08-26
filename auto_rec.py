import pyaudio
import wave
import time
import os
from pydub import AudioSegment
from src.config import path

def record_audio(duration, filename):
    # Audio recording parameters
    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 1
    fs = 44100  # Record at 44100 samples per second
    p = pyaudio.PyAudio()

    print(f"Recording {duration} seconds of audio to {filename}...")

    # Open the stream
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    frames = []

    # Record for the given duration
    for _ in range(0, int(fs / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    # Stop and close the stream
    stream.stop_stream()
    stream.close()

    # Terminate the PortAudio interface
    p.terminate()

    # Save the recorded data as a WAV file
    wav_filename = filename + '.wav'
    wf = wave.open(wav_filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

    # Convert the WAV file to MP3 using pydub
    audio = AudioSegment.from_wav(wav_filename)
    mp3_filename = filename + '.mp3'
    audio.export(mp3_filename, format="mp3")

    # Remove the temporary WAV file
    os.remove(wav_filename)

    print(f"Saved {mp3_filename}")

def record_at_intervals(duration, interval, output_folder, file_prefix):
    count = 0
    while True:
        filename = os.path.join(output_folder, f"{file_prefix}_{count}")
        record_audio(duration, filename)
        count += 1
        time.sleep(interval)

# 使用例
output_folder = path.PATH_INPUT
file_prefix = "recording"
duration = 30  # 録音する秒数
interval = 60  # 録音する間隔（秒）

record_at_intervals(duration, interval, output_folder, file_prefix)
