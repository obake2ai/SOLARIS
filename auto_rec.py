from src.config import path

from pydub import AudioSegment
import subprocess
import os
import time

def record_audio(duration, filename):
    # arecordを使って録音
    wav_filename = filename + '.wav'
    command = [
        'arecord',
        '-D', 'hw:1,0',  # デバイスIDを指定
        '-f', 'cd',  # フォーマット：16-bit little-endian, 44100Hz, ステレオ
        '-t', 'wav',
        '-c', '1',
        '-d', str(duration),  # 録音時間
        wav_filename
    ]

    print(f"{duration}秒間のオーディオを{filename}に録音しています...")

    # arecordコマンドを実行して録音
    subprocess.run(command, check=True)

    # pydubを使用してWAVファイルをMP3に変換
    audio = AudioSegment.from_wav(wav_filename)
    mp3_filename = filename + '.mp3'
    audio.export(mp3_filename, format="mp3")

    # 一時的なWAVファイルを削除
    os.remove(wav_filename)

    print(f"{mp3_filename}に保存されました")

def record_at_intervals(duration, interval, output_folder, file_prefix):
    while True:
        filename = os.path.join(output_folder, f"{file_prefix}")
        record_audio(duration, filename)
        time.sleep(interval)

# 使用例
output_folder = path.PATH_INPUT
file_prefix = "recording"
duration = 10  # 録音する秒数
interval = 60  # 録音する間隔（秒）

# 出力フォルダが存在しない場合は作成
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

record_at_intervals(duration, interval, output_folder, file_prefix)
