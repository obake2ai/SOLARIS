import pyaudio
import wave
import time
import os
from pydub import AudioSegment
from src.config import path

def record_audio(duration, filename):
    # オーディオ録音のパラメータ
    chunk = 4096  # チャンクサイズを増やしてオーバーフローを防ぐ
    sample_format = pyaudio.paInt16  # 16ビットサンプル
    channels = 1
    fs = 44100  # 44100Hzで録音
    p = pyaudio.PyAudio()

    print(f"{duration}秒間のオーディオを{filename}に録音しています...")

    # ストリームを開く
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True,
                    input_device_index=1,  # 必要に応じて入力デバイスを指定
                    stream_callback=None,
                    start=True)

    frames = []

    # 指定された期間録音する
    for _ in range(0, int(fs / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    # ストリームを停止し閉じる
    stream.stop_stream()
    stream.close()

    # PortAudioインターフェースを終了
    p.terminate()

    # 録音したデータをWAVファイルとして保存
    wav_filename = filename + '.wav'
    wf = wave.open(wav_filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

    # pydubを使用してWAVファイルをMP3に変換
    audio = AudioSegment.from_wav(wav_filename)
    mp3_filename = filename + '.mp3'
    audio.export(mp3_filename, format="mp3")

    # 一時的なWAVファイルを削除
    os.remove(wav_filename)

    print(f"{mp3_filename}に保存されました")

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
duration = 5  # 録音する秒数
interval = 60  # 録音する間隔（秒）

record_at_intervals(duration, interval, output_folder, file_prefix)
