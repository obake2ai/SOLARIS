from src.config import path, imagen_config
from pydub import AudioSegment
import subprocess
import os
import time
import shutil
from datetime import datetime

def record_audio(duration, tmp_filename):
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

    print(f"[{datetime.now()}] Recording audio for {duration} seconds to {tmp_filename}...")

    subprocess.run(command, check=True)

    audio = AudioSegment.from_wav(wav_filename)
    mp3_filename = tmp_filename + '.mp3'
    audio.export(mp3_filename, format="mp3")

    os.remove(wav_filename)

    return mp3_filename

def move_to_output(tmp_filename, output_filename):
    shutil.move(tmp_filename, output_filename)
    print(f"[{datetime.now()}] Moved to {output_filename}")

def delete_old_files(folder, limit=100):
    files = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    if len(files) > limit:
        files.sort(key=os.path.getmtime)
        files_to_delete = files[:len(files) - limit]
        for file in files_to_delete:
            os.remove(file)
            print(f"[{datetime.now()}] Deleted old file {file}")

def record_at_intervals(duration, interval, tmp_folder, output_folder, file_prefix):
    counter = 0
    while True:
        counter += 1
        tmp_filename = os.path.join(tmp_folder, f"{file_prefix}")
        output_filename = os.path.join(output_folder, f"{file_prefix}_{str(counter).zfill(6)}.mp3")

        tmp_mp3_filename = record_audio(duration, tmp_filename)

        move_to_output(tmp_mp3_filename, output_filename)
        os.chmod(output_filename, 0o666)

        delete_old_files(output_folder, limit=100)

        time.sleep(interval)

# 使用例
tmp_folder = path.PATH_TMP
output_folder = path.PATH_INPUT
file_prefix = "recording"
duration = imagen_config.AUDIO_LENGTH
interval = imagen_config.AUDIO_INTERVAL

if not os.path.exists(tmp_folder):
    os.makedirs(tmp_folder)

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

record_at_intervals(duration, interval, tmp_folder, output_folder, file_prefix)
