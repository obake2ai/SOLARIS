#!/bin/bash

# Dockerコンテナの存在確認と起動
if [ "$(docker ps -q -f name=solaris02)" ]; then
    echo "solaris is already running."
else
    echo "solaris is opening..."
    docker start solaris02
fi

# 画面の解像度を取得
SCREEN_WIDTH=$(xrandr | grep '*' | awk '{print $1}' | cut -d'x' -f1)
SCREEN_HEIGHT=$(xrandr | grep '*' | awk '{print $1}' | cut -d'x' -f2)

# ターミナルウィンドウのサイズと位置を計算
TERM_WIDTH=$((SCREEN_WIDTH / 4))
TERM_HEIGHT=$((SCREEN_HEIGHT / 4))

# ターミナル1: 左上
gnome-terminal --geometry=${TERM_WIDTH}x${TERM_HEIGHT}+0+0 -- bash -c "docker exec -it solaris02 bash -c 'cd ~/Share/SOLARIS/ && python3 RUN_monitor.py ./audio_handler.py'; exec bash"

# ターミナル2: 右上
gnome-terminal --geometry=${TERM_WIDTH}x${TERM_HEIGHT}+$((SCREEN_WIDTH - TERM_WIDTH))+0 -- bash -c "docker exec -it solaris02 bash -c 'cd ~/Share/SOLARIS/ && watch -n 5 nvidia-smi'; exec bash"

# 60秒間待機
sleep 60

# ターミナル3: 左下
gnome-terminal --geometry=${TERM_WIDTH}x${TERM_HEIGHT}+0+$((SCREEN_HEIGHT - TERM_HEIGHT)) -- bash -c "docker exec -it solaris02 bash -c 'cd ~/Share/SOLARIS/ && python3 RUN_monitor.py ./auto_rec.py'; exec bash"

# ターミナル4: 右下
gnome-terminal --geometry=${TERM_WIDTH}x${TERM_HEIGHT}+$((SCREEN_WIDTH - TERM_WIDTH))+$((SCREEN_HEIGHT - TERM_HEIGHT)) -- bash -c "cd ~/Share/SOLARIS/ && python3 RUN_monitor.py /home/yuma/Share/SOLARIS/solaris_preview.py; exec bash"
