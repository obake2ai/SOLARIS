import os
import time
import sys
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib import rcParams
from src.config import path

def get_latest_image(folder_path):
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
    if not files:
        return None
    latest_file = max(files, key=os.path.getctime)
    return latest_file

def display_image(ax, image_path):
    img = Image.open(image_path)
    img = img.resize((fig.canvas.get_width_height()), Image.ANTIALIAS)  # 画像をウィンドウサイズにスケーリング
    ax.clear()  # 余白が残らないようにクリア
    ax.imshow(img)
    ax.axis('off')  # 軸を非表示
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)  # 余白を取り除く
    plt.draw()
    plt.pause(1/24)  # 1/24秒待機

def main(folder_path):
    plt.ion()  # インタラクティブモードをオンにする
    global fig, ax
    fig, ax = plt.subplots()
    mng = plt.get_current_fig_manager()
    mng.full_screen_toggle()  # フルスクリーンモードにする
    fig.canvas.toolbar_visible = False  # ツールバーを非表示
    fig.canvas.header_visible = False  # ヘッダーを非表示
    fig.canvas.footer_visible = False  # フッターを非表示
    fig.canvas.mpl_connect('key_press_event', on_key)

    while True:
        latest_image = get_latest_image(folder_path)
        if latest_image:
            display_image(ax, latest_image)
        time.sleep(1/24)  # 1/24秒ごとに画像を更新

def on_key(event):
    if event.key == 'q':
        plt.close(fig)
        sys.exit(0)  # プログラムを終了

if __name__ == "__main__":
    folder_path = path.PATH_OUTPUT
    main(folder_path)
