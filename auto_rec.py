from src.config import path

from pydub import AudioSegment
import subprocess
import os
import time

def record_audio(duration, filename):
    # 録音コマンド
    command = [
        'ffmpeg',
        '-f', 'alsa',  # ALSAを使用する
        '-i', 'hw:1,0',  # デバイスのIDを指定 (arecord -lで確認したものに合わせる)
        '-t', str(duration),  # 録音時間
        '-acodec', 'pcm_s16le',  # 音声コーデック（WAVフォーマット）
        filename + '.wav'  # 出力ファイル名
    ]

    print(f"{duration}秒間のオーディオを{filename}に録音しています...")

    # ffmpegコマンドを実行して録音
    subprocess.run(command, check=True)

    # pydubを使用してWAVファイルをMP3に変換
    audio = AudioSegment.from_wav(filename + '.wav')
    audio.export(filename + '.mp3', format="mp3")

    # 一時的なWAVファイルを削除
    os.remove(filename + '.wav')

    print(f"{filename}.mp3 に保存されました")

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
