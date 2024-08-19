from imagen_pytorch import load_imagen_from_checkpoint, ImagenTrainer, Unet, Imagen, ElucidatedImagenConfig, ImagenConfig, UnetConfig, ElucidatedImagen
import torch
from config import path, imagen_config
from faster_whisper import WhisperModel as WM
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class ImagenModel:
    def __init__(self, checkpoint_path, image_size, timesteps):
        self.checkpoint_path = checkpoint_path
        self.image_size = image_size
        self.timesteps = timesteps
        self.imagen = self.load_imagen()

    def load_imagen(self):
        unet = Unet(
            dim=32,
            dim_mults=(1, 2, 4, 8),
            num_resnet_blocks=1,
            layer_attns=(False, False, False, True),
            layer_cross_attns=False
        )

        imagen = Imagen(
            condition_on_text=False,  # this must be set to False for unconditional Imagen
            unets=unet,
            image_sizes=self.image_size,
            timesteps=self.timesteps
        )

        checkpoint = torch.load(self.checkpoint_path)
        imagen.load_state_dict(checkpoint['model'])
        return imagen

    def generate_image(self, prompt):
        images = self.imagen.sample(texts=[prompt],
                                    batch_size=1, return_pil_images=True)
        return images[0]

class WhisperModel:
    def __init__(self):
        self.checkpoint_path = None
        self.whisper = self.load_whisper()

    def load_whisper(self):
        model = WM("medium", device="cuda" if torch.cuda.is_available() else "cpu")
        return model

    def transcribe_audio2text(self, audio_file):
        segments, info = self.whisper.transcribe(audio_file)
        for segment in segments:
            print(f"[{segment.start:.2f}s - {segment.end:.2f}s] {segment.text}")

        return segment.text

def test_imagen(prompt=None):
    imagen_config = {
        'SIZE_IMAGEN': 128,
        'TIMESTEPS_IMAGEN': 100,
        'PATH_IMAGEN': path.PATH_IMAGEN,
        'PATH_OUTPUT': path.PATH_OUTPUT,
    }

    model = ImagenModel(checkpoint_path=imagen_config['PATH_IMAGEN'],
                        image_size=imagen_config['SIZE_IMAGEN'],
                        timesteps=imagen_config['TIMESTEPS_IMAGEN'])

    if not prompt:
        prompt = "Example prompt text"
    generated_image = model.generate_image(prompt)
    generated_image.save(f"{imagen_config['PATH_OUTPUT']}/sample_{prompt}.png")


def test_whisper():
    whisper_config = {
        'PATH_AUDIOFILE': path.PATH_AUDIOFILE,
        'PATH_OUTPUT': path.PATH_OUTPUT,
    }

    model = WhisperModel()
    transcribe_text = model.transcribe_audio2text(whisper_config['PATH_AUDIOFILE'])
    check_txtfile = f"{whisper_config['PATH_OUTPUT']}/sample.txt"
    with open(check_txtfile, 'w') as f:
        f.write(transcribe_text)
    return transcribe_text

def test_whisper_imagen():
    transcribe_text = test_whisper()
    test_imagen(transcribe_text)


if __name__ == '__main__':
    #test_imagen()
    # test_whisper()
    test_whisper_imagen()
