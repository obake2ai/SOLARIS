from config import path, imagen_config
from pydub import AudioSegment
import subprocess
import os
import time
import shutil
from datetime import datetime, time as dt_time
import pytz  # pytzをインポート

# JSTのタイムゾーンを設定
jst = pytz.timezone('Asia/Tokyo')

def get_jst_now():
    """現在のJST時刻を取得する関数"""
    return datetime.now(jst)

def record_audio(duration, tmp_filename):
    wav_filename = tmp_filename + '.wav'
    channels = 1  # 初期設定は1チャンネル（モノラル）
    device_name = 'plughw:CARD=Microphone,DEV=0'  # 例：USBマイクの設定

    while True:
        command = [
            'arecord',
            '-D', device_name,  # デバイス名を設定
            '-f', 'cd',  # フォーマット：16-bit little-endian, 44100Hz, ステレオ
            '-t', 'wav',
            '-c', str(channels),  # チャンネル数
            '-d', str(duration),  # 録音時間
            wav_filename
        ]

        print(f"[{get_jst_now()}] Recording audio for {duration} seconds to {tmp_filename} with {channels} channel(s) using {device_name}...")

        try:
            subprocess.run(command, check=True)
            break  # 録音成功時はループを抜ける
        except subprocess.CalledProcessError as e:
            if "Device or resource busy" in str(e):
                print(f"[{get_jst_now()}] Device is busy, skipping this interval.")
                return None
            elif "Channels count non available" in str(e):
                print(f"[{get_jst_now()}] Channel count not available for this device. Trying with different channel count.")
                if channels == 1:
                    channels = 2  # モノラルがダメならステレオを試す
                else:
                    print(f"[{get_jst_now()}] No suitable channel count available. Skipping this interval.")
                    return None
            else:
                print(f"[{get_jst_now()}] An error occurred: {e}")
                return None

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
    print(f"[{get_jst_now()}] Moved to {output_filename}")

def delete_old_files(folder, limit=100):
    files = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    if len(files) > limit:
        files.sort(key=os.path.getmtime)
        files_to_delete = files[:len(files) - limit]
        for file in files_to_delete:
            os.remove(file)
            print(f"[{get_jst_now()}] Deleted old file {file}")

def resolve_busy_device():
    print(f"[{get_jst_now()}] Resolving device busy state...")
    # 例: デバイスのリセットや他のプロセスの終了
    # os.system("sudo fuser -k /dev/snd/*")

def record_at_intervals(duration, interval, tmp_folder, output_folder, file_prefix, start_time, end_time):
    counter = 0
    skip_count = 0  # スキップ回数をカウント

    while True:
        # 現在の時刻をJSTに変換
        current_time = get_jst_now().time()

        if current_time < start_time or current_time > end_time:
            print(f"[{get_jst_now()}] Outside of scheduled recording time (JST). Skipping...")
            time.sleep(interval)
            continue

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
start_time = dt_time(12, 5, 0)  # 録音開始時刻：8:00 AM JST
end_time = dt_time(12, 15, 0)   # 録音終了時刻：12:00 PM JST（正午）

if not os.path.exists(tmp_folder):
    os.makedirs(tmp_folder)

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

record_at_intervals(duration, interval, tmp_folder, output_folder, file_prefix, start_time, end_time)
