import os
import time
import sys
import pygame
from pygame.locals import QUIT, KEYDOWN, K_q
from src.config import path

def get_latest_image(folder_path):
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
    if not files:
        return None
    latest_file = max(files, key=os.path.getctime)
    return latest_file

def display_image(screen, image_path):
    img = pygame.image.load(image_path)
    img = pygame.transform.scale(img, screen.get_size())  # 画像を画面サイズにスケーリング
    screen.blit(img, (0, 0))
    pygame.display.flip()

def main(folder_path):
    pygame.init()
    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_q):
                pygame.quit()
                sys.exit(0)

        latest_image = get_latest_image(folder_path)
        if latest_image:
            display_image(screen, latest_image)
        time.sleep(1/24)  # 1/24秒ごとに画像を更新

if __name__ == "__main__":
    folder_path = path.PATH_OUTPUT
    main(folder_path)
