import time
import os
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from config import path, imagen_config
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
        if event.src_path.endswith((".mp3", ".wav")):
            print(f"New Audio file created: {event.src_path}")
            if self.wait_for_file_creation(event.src_path):
                self.process_file(event.src_path)
            else:
                print("File creation did not stabilize within timeout.")

    def on_modified(self, event):
        print(f"on_modified called for: {event.src_path}")
        if event.is_directory:
            return
        if event.src_path.endswith((".mp3", ".wav")):
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
                self.index_1 += 1
            else:
                self.index_1 = 0

    def wait_for_file_creation(self, filepath, timeout=imagen_config.AUDIO_LENGTH):
        previous_size = -1
        start_time = time.time()

        while time.time() - start_time < timeout:
            current_size = os.path.getsize(filepath)
            if current_size == previous_size:
                return True
            previous_size = current_size
            time.sleep(0.5)

        return False

def monitor_observer(observer):
    while True:
        if not observer.is_alive():
            print("Observer stopped, restarting...")
            observer.stop()
            observer.join()
            observer.start()
        time.sleep(5)

def watch_folder(folder_path):
    # Load models once
    whisper_model = functions.WhisperModel()
    imagen_model = functions.ImagenModel(
        checkpoint_path=path.PATH_IMAGEN,
        image_size=imagen_config.SIZE_IMAGEN,
        timesteps=imagen_config.TIMESTEPS_IMAGEN
    )

    event_handler = AudioEventHandler(folder_path, whisper_model, imagen_model)
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=True)
    observer.start()

    observer_thread = threading.Thread(target=monitor_observer, args=(observer,))
    observer_thread.daemon = True
    observer_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    print("Launching...")
    folder_to_watch = path.PATH_INPUT
    watch_folder(folder_to_watch)
