from imagen_pytorch import load_imagen_from_checkpoint, ImagenTrainer, Unet, Imagen, ElucidatedImagenConfig, ImagenConfig, UnetConfig, ElucidatedImagen
import torch
from .config import path, imagen_config
from faster_whisper import WhisperModel as WM
import sys
import os
from PIL import ImageDraw, ImageFont, ImageEnhance
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class ImagenModel:
    def __init__(self, checkpoint_path, image_size, timesteps, font_path):
        self.checkpoint_path = checkpoint_path
        self.image_size = image_size
        self.timesteps = timesteps
        self.font_path = path.PATH_FONT_EN
        self.caption_x = imagen_config.CAPTION_X
        self.caption_y = imagen_config.CAPTION_Y
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

    def generate_image(self, prompt, text_position=(10, 10)):
        images = self.imagen.sample(texts=[prompt],
                                    batch_size=1, return_pil_images=True)
        image = images[0].resize((imagen_config.RESIZE_WIDTH, imagen_config.RESIZE_HEIGHT))
        return self.add_caption(image, prompt, text_position)

    def add_caption(self, image, prompt, text_position):
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(self.font_path, size=40)

        # Calculate the brightness of the image
        grayscale_image = image.convert("L")
        brightness = np.array(grayscale_image).mean()

        # Determine text color based on brightness
        text_color = "white" if brightness < 128 else "black"

        # Add text to the image at the specified position
        draw.text(text_position, prompt, fill=text_color, font=font)

        return image

class WhisperModel:
    def __init__(self):
        self.checkpoint_path = None
        self.whisper = self.load_whisper()

    def load_whisper(self):
        model = WM("medium", device="cuda" if torch.cuda.is_available() else "cpu")
        return model

    def transcribe_audio2text(self, audio_file):
        segments, info = self.whisper.transcribe(audio_file)
        full_text = ''.join(segment.text for segment in segments)
        detected_language = info['language']

        print(f"Detected Language: {detected_language}")
        print(f"Detected Text: {full_text}")

        return full_text, detected_language

def test_imagen(prompt=None):
    imagen_config = {
        'SIZE_IMAGEN': 128,
        'TIMESTEPS_IMAGEN': 500,
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
