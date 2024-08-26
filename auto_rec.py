from src.config import path

from pydub import AudioSegment
import subprocess
import os
import time
import shutil

def record_audio(duration, tmp_filename):
    # arecordを使って録音
    wav_filename = tmp_filename + '.wav'
    command = [
        'arecord',
        '-D', 'hw:1,0',  # デバイスIDを指定
        '-f', 'cd',  # フォーマット：16-bit little-endian, 44100Hz, ステレオ
        '-t', 'wav',
        '-c', '1',
        '-d', str(duration),  # 録音時間
        wav_filename
    ]

    print(f"Recording audio for {duration} seconds to {tmp_filename}...")

    # arecordコマンドを実行して録音
    subprocess.run(command, check=True)

    # pydubを使用してWAVファイルをMP3に変換
    audio = AudioSegment.from_wav(wav_filename)
    mp3_filename = tmp_filename + '.mp3'
    audio.export(mp3_filename, format="mp3")

    # 一時的なWAVファイルを削除
    os.remove(wav_filename)

    return mp3_filename

def move_to_output(tmp_filename, output_filename):
    # ファイルをtmpからoutputフォルダに移動
    shutil.move(tmp_filename, output_filename)
    print(f"Moved to {output_filename}")

def record_at_intervals(duration, interval, tmp_folder, output_folder, file_prefix):
    while True:
        tmp_filename = os.path.join(tmp_folder, f"{file_prefix}")
        output_filename = os.path.join(output_folder, f"{file_prefix}.mp3")

        tmp_mp3_filename = record_audio(duration, tmp_filename)

        move_to_output(tmp_mp3_filename, output_filename)

        time.sleep(interval)

# 使用例
tmp_folder = path.PATH_TMP
output_folder = path.PATH_INPUT
file_prefix = "recording"
duration = 10  # 録音する秒数
interval = 60  # 録音する間隔（秒）

# tmpフォルダとoutputフォルダが存在しない場合は作成
if not os.path.exists(tmp_folder):
    os.makedirs(tmp_folder)

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

record_at_intervals(duration, interval, tmp_folder, output_folder, file_prefix)
