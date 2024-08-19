from imagen_pytorch import load_imagen_from_checkpoint, ImagenTrainer, Unet, Imagen, ElucidatedImagenConfig, ImagenConfig, UnetConfig, ElucidatedImagen
import torch
from ..config import path, imagen_config

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

def test_imagen():
    imagen_config = {
        'SIZE_IMAGEN': 128,
        'TIMESTEPS_IMAGEN': 1000,
    }

    path = {
        'PATH_IMAGEN': imagen_config.PATH_IMAGEN
    }

    # クラスを初期化して使用
    model = ImagenModel(checkpoint_path=path['PATH_IMAGEN'],
                        image_size=imagen_config['SIZE_IMAGEN'],
                        timesteps=imagen_config['TIMESTEPS_IMAGEN'])

    # 画像を生成
    prompt = "Example prompt text"
    generated_image = model.generate_image(prompt)
    generated_image.show()
