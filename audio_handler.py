import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.config import path

class MP3EventHandler(FileSystemEventHandler):
    def __init__(self, folder_path):
        self.folder_path = folder_path

    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(".mp3"):
            relative_path = os.path.relpath(event.src_path, self.folder_path)
            print(f"Updated MP3 file: {relative_path}")

def watch_folder(folder_path):
    event_handler = MP3EventHandler(folder_path)
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    folder_to_watch = path.PATH_INPUT
    watch_folder(folder_to_watch)
