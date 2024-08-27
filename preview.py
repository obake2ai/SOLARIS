import os
import time
from PIL import Image
import matplotlib.pyplot as plt
from src.config import path

def get_latest_image(folder_path):
    """フォルダ内の最新の画像ファイルを取得"""
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
    if not files:
        return None
    latest_file = max(files, key=os.path.getctime)
    return latest_file

def display_image(ax, image_path):
    """画像を表示"""
    img = Image.open(image_path)
    ax.imshow(img)
    plt.draw()
    plt.pause(1/24)  # 1/24秒待機

def main(folder_path):
    """メインループ"""
    plt.ion()  # インタラクティブモードをオンにする
    fig, ax = plt.subplots()
    while True:
        latest_image = get_latest_image(folder_path)
        if latest_image:
            display_image(ax, latest_image)
        time.sleep(1/24)  # 1/24秒ごとに画像を更新

if __name__ == "__main__":
    folder_path = path.PATH_OUTPUT
    main(folder_path)
