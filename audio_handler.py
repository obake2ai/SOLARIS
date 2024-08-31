import time
import os
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.config import path, imagen_config
from src import functions
from run_imagen import run_imagen  # Import the function directly

class AudioEventHandler(FileSystemEventHandler):
    def __init__(self, folder_path, whisper_model, imagen_model):
        self.folder_path = folder_path
        self.whisper_model = whisper_model
        self.imagen_model = imagen_model
        self.index_1 = 0
        self.index_2 = 0
        self.output_path = path.PATH_OUTPUT
        self.last_processed_file = None  # 最新の処理済みファイルを追跡
        print("Initial setup complete...Waiting for audio input...")

    def on_created(self, event):
        print(f"on_created called for: {event.src_path}")
        if event.is_directory:
            return
        if event.src_path.endswith((".mp3", ".wav")):  # .mp3または.wavの場合に処理
            print(f"New Audio file created: {event.src_path}")
            if self.wait_for_file_creation(event.src_path):
                self.process_file(event.src_path)
            else:
                print("File creation did not stabilize within timeout.")

    def on_modified(self, event):
        print(f"on_modified called for: {event.src_path}")
        if event.is_directory:
            return
        if event.src_path.endswith((".mp3", ".wav")):  # .mp3または.wavの場合に処理
            print(f"Updated Audio file: {event.src_path}")
            if self.wait_for_file_creation(event.src_path):
                self.process_file(event.src_path)
            else:
                print("File modification did not stabilize within timeout.")

    def process_file(self, audio_path):
        # ファイルが以前に処理されたものと異なる場合のみ処理を行う
        if self.last_processed_file != audio_path:
            try:
                # Use the loaded models to process audio and generate image
                output_index = f"{self.index_1}-{self.index_2}"  # 生成する画像のファイル名を設定
                run_imagen(audio_path, self.whisper_model, self.imagen_model, self.output_path, output_index)
                self.last_processed_file = audio_path  # 現在のファイル名を記憶
                self.update_indices()  # インデックスを更新
            except Exception as e:
                print(f"Error processing audio file: {e}")
        else:
            print(f"Skipping file {audio_path} as it is already processed.")

    def update_indices(self):
        # インデックスを更新するロジック
        if self.index_2 < 99:
            self.index_2 += 1
        else:
            self.index_2 = 0
            if self.index_1 < 99:
