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
    def __init__(self, checkpoint_path, image_size, timesteps):
        self.checkpoint_path = checkpoint_path
        self.image_size = image_size
        self.timesteps = timesteps
        self.font_path_ja = path.PATH_FONT_JA
        self.font_path_en = path.PATH_FONT_EN
        self.font_path_idx = path.PATH_FONT_IDX
        self.caption_x = imagen_config.CAPTION_X
        self.caption_y = imagen_config.CAPTION_Y
        self.font_size = imagen_config.CAPTION_SIZE
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

    def generate_image(self, prompt, index, lang='ja'):
        text_position = (self.caption_x, self.caption_y)
        images = self.imagen.sample(texts=[prompt],
                                    batch_size=1, return_pil_images=True)
        image = images[0].resize((imagen_config.RESIZE_WIDTH, imagen_config.RESIZE_HEIGHT))
        return self.add_caption(image, prompt, index, text_position, lang)

    def add_caption(self, image, prompt, index, text_position, lang='ja'):
        draw = ImageDraw.Draw(image)

        font_idx = ImageFont.truetype(self.font_path_idx, size=self.font_size)

        if lang == 'ja':
            font_prompt = ImageFont.truetype(self.font_path_ja, size=self.font_size)
        else:
            font_prompt = ImageFont.truetype(self.font_path_en, size=self.font_size)

        # Calculate the brightness of the image
        grayscale_image = image.convert("L")
        brightness = np.array(grayscale_image).mean()

        # Determine text color based on brightness
        text_color = "white" if brightness < 128 else "black"

        # Calculate the width of the image
        image_width, _ = image.size
        third_of_width = image_width // 3

        # Calculate the exact position for the index text to be centered in the leftmost third
        index_x = third_of_width // 2  # Center position of the leftmost third
        index_position = (index_x, text_position[1])

        # Add the index to the image, centered in the leftmost third
        draw.text(index_position, index, fill=text_color, font=font_idx, anchor="mm")  # 'mm' for middle alignment

        # Handle prompt text: split into two lines if it exceeds width
        max_width = image_width - text_position[0] - 20  # Leave some margin
        words = list(prompt)

        # Break into two lines if necessary
        for i in range(len(words)):
            current_text = ''.join(words[:i + 1])
            bbox = draw.textbbox((0, 0), current_text, font=font_prompt)
            width = bbox[2] - bbox[0]

            if width > max_width:
                # Try to split at a natural point
                split_index = i
                for j in range(i, max(0, i - 10), -1):
                    if words[j] in ('、', '。', '　', ',', '.'):
                        split_index = j + 1
                        break
                # Split the text
                line1 = ''.join(words[:split_index])
                line2 = ''.join(words[split_index:])

                # If the second line is still too long, cut it as well
                while True:
                    bbox2 = draw.textbbox((0, 0), line2, font=font_prompt)
                    width2 = bbox2[2] - bbox2[0]
                    if width2 <= max_width:
                        break
                    for j in range(len(line2) - 1, max(0, len(line2) - 10), -1):
                        if line2[j] in ('、', '。', '　', ',', '.'):
                            split_index2 = j + 1
                            line2 = line2[:split_index2]
                            break
                    else:
                        line2 = line2[:max_width]

                # Draw the two lines
                draw.text(text_position, line1, fill=text_color, font=font_prompt, anchor="lm")
                draw.text((text_position[0], text_position[1] + self.font_size), line2, fill=text_color, font=font_prompt, anchor="lm")
                break
        else:
            # If the text fits in one line
            draw.text(text_position, prompt, fill=text_color, font=font_prompt, anchor="lm")

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
        detected_list = []
        for segment in segments:
            print(f"[{segment.start:.2f}s - {segment.end:.2f}s] {segment.text}")
            detected_list.append(segment.text)

        detected_text = ' '.join(detected_list)

        return detected_text, info.language

    # def transcribe_audio2text(self, audio_file):
    #     segments, info = self.whisper.transcribe(audio_file)
    #
    #     # Check the type and content of info
    #     print(f"Info type: {type(info)}")
    #     print(f"Info content: {info}")
    #
    #     if isinstance(info, dict):
    #         detected_language = info['language']
    #     else:
    #         # Handle the case where info is not a dict
    #         detected_language = "Unknown"
    #
    #     full_text = ''.join(segment.text for segment in segments)
    #
    #     print(f"Detected Language: {detected_language}")
    #     print(f"Detected Text: {full_text}")
    #
    #     return full_text, detected_language


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
