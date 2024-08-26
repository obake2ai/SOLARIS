
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import os
import time
from pydub import AudioSegment
from src.config import path

def record_audio(duration, filename):
    # サンプルレートの設定
    fs = 44100  # 44100Hzで録音

    print(f"{duration}秒間のオーディオを{filename}に録音しています...")

    # 録音
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2, dtype='int16')
    sd.wait()  # 録音終了まで待機

    # WAVファイルとして保存
    wav_filename = filename + '.wav'
    wav.write(wav_filename, fs, recording)

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

# 出力フォルダが存在しない場合は作成
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

record_at_intervals(duration, interval, output_folder, file_prefix)
