import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.config import path, imagen_config

from src import functions

class MP3EventHandler(FileSystemEventHandler):
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.size_imagen = imagen_config.SIZE_IMAGEN
        self.timesteps_imagen = imagen_config.TIMESTEPS_IMAGEN
        self.model_imagen = path.PATH_IMAGEN
        self.path_output = path.PATH_OUTPUT

    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(".mp3"):
            print(f"Updated MP3 file: {event.src_path}")
            # self.start_whisper()

    def start_whisper(self, audio_path):
        print ("hoge")



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
