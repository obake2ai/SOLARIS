import os
import time
import sys
import shutil
import numpy as np
from PIL import Image
import pygame
from pygame.locals import QUIT, KEYDOWN, K_q
from src.config import path

def get_latest_image(folder_path):
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
    if not files:
        return None
    latest_file = max(files, key=os.path.getctime)
    return latest_file

def blend_images(img1_path, img2_path, duration, fps):
    img1 = Image.open(img1_path)
    img2 = Image.open(img2_path)

    img1 = np.array(img1)
    img2 = np.array(img2)

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

        blended_images.append(blended)

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

def main(watch_folder, preview_folder, transition_duration=2, fps=24):
    pygame.init()
    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)

    previous_image = None
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_q):
                pygame.quit()
                sys.exit(0)

        latest_image_path = get_latest_image(watch_folder)
        if latest_image_path and (previous_image is None or latest_image_path != previous_image):
            new_image_path = os.path.join(preview_folder, os.path.basename(latest_image_path))
            shutil.copy(latest_image_path, new_image_path)

            if previous_image:
                transition_images = blend_images(previous_image, new_image_path, transition_duration, fps)
                for blended_img in transition_images:
                    display_image(screen, blended_img)
                    time.sleep(1 / fps)
            else:
                img = Image.open(new_image_path)
                img = img.resize(screen.get_size(), Image.ANTIALIAS)
                display_image(screen, np.array(img))

            previous_image = new_image_path

        time.sleep(1 / fps)

if __name__ == "__main__":
    watch_folder = path.PATH_OUTPUT
    preview_folder = path.PATH_PREVIEW 
    main(watch_folder, preview_folder)
