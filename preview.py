import os
import time
from PIL import Image
import matplotlib.pyplot as plt
from src.config import path

def get_latest_image(folder_path):
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
    if not files:
        return None
    latest_file = max(files, key=os.path.getctime)
    return latest_file

def display_image(image_path):
    img = Image.open(image_path)
    plt.imshow(img)
    plt.axis('off')
    plt.show(block=False)
    plt.pause(1/24)
    plt.close()

def main(folder_path):
    while True:
        latest_image = get_latest_image(folder_path)
        if latest_image:
            display_image(latest_image)
        time.sleep(1/24)

if __name__ == "__main__":
    folder_path = path.PATH_OUTPUT
    main(folder_path)
