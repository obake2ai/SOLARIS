import os
import time
import sys
import shutil
import numpy as np
from PIL import Image, UnidentifiedImageError
import pygame
from pygame.locals import QUIT, KEYDOWN, K_q
from config import path, imagen_config

def get_latest_image(folder_path):
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
    if not files:
        return None
    latest_file = max(files, key=os.path.getctime)
    return latest_file

def blend_images(img1_path, img2_path, duration, fps):
    img1 = np.asarray(safe_image_open(img1_path))
    img2 = np.asarray(safe_image_open(img2_path))

    total_pixels = img1.shape[0] * img1.shape[1]
    num_frames = int(fps * duration)
    pixels_per_frame = total_pixels // num_frames

    indices = np.arange(total_pixels)
    np.random.shuffle(indices)

    blended_images = []

    blended = img1.copy()
    for frame_num in range(1, num_frames + 1):
        num_pixels_to_change = pixels_per_frame * frame_num
        current_indices = indices[:num_pixels_to_change]

        flat_blended = blended.reshape(-1, 3)
        flat_img2 = img2.reshape(-1, 3)

        flat_blended[current_indices] = flat_img2[current_indices]
        blended = flat_blended.reshape(img1.shape)

        blended_images.append(blended.copy())

    return blended_images

def display_image(screen, image_array):
    img = Image.fromarray(image_array)
    img = img.resize(screen.get_size(), Image.ANTIALIAS)
    mode = img.mode
    size = img.size
    data = img.tobytes()

    pygame_image = pygame.image.fromstring(data, size, mode)
    screen.blit(pygame_image, (0, 0))
    pygame.display.flip()

def safe_image_open(path, retries=5, delay=0.5):
    for _ in range(retries):
        try:
            return Image.open(path)
        except (OSError, UnidentifiedImageError):
            time.sleep(delay)
    print(f"Warning: Unable to open image file after {retries} retries: {path}")
    return None

def main(watch_folder, preview_folder, transition_duration=imagen_config.AUDIO_INTERVAL//4, fps=24):
    pygame.init()
    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w, info.current_h))
    pygame.display.set_caption("solaris")
    clock = pygame.time.Clock()

    previous_image = None
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_q):
                running = False

        latest_image_path = get_latest_image(watch_folder)
        if latest_image_path:
            new_image_path = os.path.join(preview_folder, os.path.basename(latest_image_path))

            # 初回は単に画像を設定し、アニメーションは行わない
            if previous_image is None:
                shutil.copy(latest_image_path, new_image_path)
                img = safe_image_open(new_image_path)
                if img is None:
                    continue  # 画像が読み込めなければ次のループに進む
                img = img.resize(screen.get_size(), Image.ANTIALIAS)
                display_image(screen, np.asarray(img))
                previous_image = new_image_path
            elif latest_image_path != previous_image:
                shutil.copy(latest_image_path, new_image_path)
                img1 = safe_image_open(previous_image)
                img2 = safe_image_open(new_image_path)
                if img1 is None or img2 is None:
                    previous_image = new_image_path
                    continue  # 画像が読み込めなければ次のループに進む
                transition_images = blend_images(previous_image, new_image_path, transition_duration, fps)
                for blended_img in transition_images:
                    display_image(screen, blended_img)
                # アニメーションが完了したら previous_image を更新
                previous_image = new_image_path

        clock.tick(fps // 2)  # メインループを適度な速さで回す

    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    watch_folder = path.PATH_OUTPUT
    preview_folder = path.PATH_PREVIEW
    main(watch_folder, preview_folder)
