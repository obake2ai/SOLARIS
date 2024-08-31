from config import path, imagen_config
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

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        if "Device or resource busy" in str(e):
            print(f"[{datetime.now()}] Device is busy, skipping this interval.")
            return None
        else:
            raise

    # 音声ファイルを読み込み
    audio = AudioSegment.from_wav(wav_filename)

    # ボリュームを底上げする（例：10dB増幅）
    #boosted_audio = audio + imagen_config.AUDIO_GAIN

    # 増幅後の音声をMP3形式でエクスポート
    mp3_filename = tmp_filename + '.mp3'
    audio.export(mp3_filename, format="mp3")

    # 一時的なWAVファイルを削除
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

def resolve_busy_device():
    # ビジー状態を解決するための処理を追加します
    print(f"[{datetime.now()}] Resolving device busy state...")
    # 例: デバイスのリセットや他のプロセスの終了
    # os.system("sudo fuser -k /dev/snd/*")  # 他のプロセスを強制終了するコマンド

def record_at_intervals(duration, interval, tmp_folder, output_folder, file_prefix):
    counter = 0
    skip_count = 0  # スキップ回数をカウント

    while True:
        counter += 1
        tmp_filename = os.path.join(tmp_folder, f"{file_prefix}")
        output_filename = os.path.join(output_folder, f"{file_prefix}_{str(counter).zfill(6)}.mp3")

        tmp_mp3_filename = record_audio(duration, tmp_filename)

        if tmp_mp3_filename is None:
            skip_count += 1
            if skip_count >= 2:
                resolve_busy_device()
            time.sleep(interval)
            continue
        else:
            skip_count = 0  # 成功した場合スキップカウントをリセット

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
