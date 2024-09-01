import time
import os
import threading
import random
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
        self.last_processed_file = None
        print("Initial setup complete...Waiting for audio input...")

    def on_created(self, event):
        print(f"on_created called for: {event.src_path}")
        if event.is_directory:
            return
        if event.src_path.endswith((".mp3", ".wav")):
            self.process_latest_file()

    def on_modified(self, event):
        print(f"on_modified called for: {event.src_path}")
        if event.is_directory:
            return
        if event.src_path.endswith((".mp3", ".wav")):
            self.process_latest_file()

    def process_latest_file(self):
        latest_file = self.get_latest_file()
        if latest_file and self.last_processed_file != latest_file:
            self.process_file(latest_file)

    def get_latest_file(self):
        try:
            files = [f for f in os.listdir(self.folder_path) if f.endswith((".mp3", ".wav"))]
            files = [os.path.join(self.folder_path, f) for f in files]
            latest_file = max(files, key=os.path.getmtime)
            return latest_file
        except ValueError:
            return None

    def process_file(self, audio_path):
        if self.last_processed_file != audio_path:
            try:
                output_index = f"{self.index_1}:{self.index_2}"
                run_imagen(audio_path, self.whisper_model, self.imagen_model, self.output_path, output_index)
                self.last_processed_file = audio_path
                self.update_indices()
            except Exception as e:
                print(f"Error processing audio file: {e}")

    def update_indices(self):
        # インデックスを0から49の間でランダムに設定
        self.index_1 = random.randint(0, 49)
        self.index_2 = random.randint(0, 49)

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
