import time
import os
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.config import path, imagen_config
from datetime import datetime
import threading

class AudioEventHandler(FileSystemEventHandler):
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.index_1 = 0
        self.index_2 = 0
        print("Initial setup complete...Waiting for audio input...")

    def on_created(self, event):
        print(f"on_created called for: {event.src_path}")
        if event.is_directory:
            return
        if event.src_path.endswith(".mp3"):
            print(f"New Audio file created: {event.src_path}")
            if self.wait_for_file_creation(event.src_path):
                self.process_file(event.src_path)
            else:
                print("File creation did not stabilize within timeout.")

    def on_modified(self, event):
        print(f"on_modified called for: {event.src_path}")
        if event.is_directory:
            return
        if event.src_path.endswith(".mp3"):
            print(f"Updated Audio file: {event.src_path}")
            if self.wait_for_file_creation(event.src_path):
                self.process_file(event.src_path)
            else:
                print("File modification did not stabilize within timeout.")

    def process_file(self, audio_path):
        try:
            # Run the external script to process audio and generate image
            subprocess.run(["python", "run_imagen.py", audio_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running run_imagen.py: {e}")

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
    event_handler = AudioEventHandler(folder_path)
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
