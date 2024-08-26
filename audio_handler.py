import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.config import path, imagen_config
from src import functions

class AudioEventHandler(FileSystemEventHandler):
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.size_imagen = imagen_config.SIZE_IMAGEN
        self.timesteps_imagen = imagen_config.TIMESTEPS_IMAGEN
        self.model_imagen = path.PATH_IMAGEN
        self.path_output = path.PATH_OUTPUT

        self.wisper = functions.WhisperModel()
        self.imagen = functions.ImagenModel(
                                checkpoint_path=self.model_imagen,
                                image_size=self.size_imagen,
                                timesteps=self.timesteps_imagen)

        print("Initial setup complete...Waiting for audio input...")

    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(".mp3"):
            print(f"New Audio file created: {event.src_path}")
            if self.wait_for_file_creation(event.src_path):
                detected_text = self.start_whisper(event.src_path)
                print((f"Detected text: {detected_text}"))
                self.start_imagen(detected_text)
            else:
                print("File creation did not stabilize within timeout.")

    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(".mp3"):
            print(f"Updated Audio file: {event.src_path}")
            if self.wait_for_file_creation(event.src_path):
                detected_text = self.start_whisper(event.src_path)
                print((f"Detected text: {detected_text}"))
                self.start_imagen(detected_text)
            else:
                print("File modification did not stabilize within timeout.")

    def start_whisper(self, audio_path):
        transcribe_text = self.wisper.transcribe_audio2text(audio_path)
        check_txtfile = f"{self.path_output}/whisper_output.txt"
        with open(check_txtfile, 'w') as f:
            f.write(transcribe_text)
        return transcribe_text

    def start_imagen(self, prompt):
        generated_image = self.imagen.generate_image(prompt)
        generated_image.save(f"{self.path_output}/imagen_output_{prompt}.png")
        print(f"Imagen saved: {self.path_output}/imagen_output_{prompt}.png")

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

def watch_folder(folder_path):
    event_handler = AudioEventHandler(folder_path)
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
    print("Launching...")
    folder_to_watch = path.PATH_INPUT
    watch_folder(folder_to_watch)
