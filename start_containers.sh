#!/bin/bash

# Dockerコンテナの存在確認と起動
if [ "$(docker ps -q -f name=solaris02)" ]; then
    echo "solaris is already running."
else
    echo "solaris is opening..."
    docker start solaris02
fi

# ターミナル1: 左上
gnome-terminal --geometry=204x54+0+0 -- bash -c "docker exec -it solaris02 bash -c 'cd ~/Share/SOLARIS/ && python3 RUN_monitor.py ./audio_handler.py'; exec bash"

# ターミナル2: 右上
gnome-terminal --geometry=204x54+1920+0 -- bash -c "docker exec -it solaris02 bash -c 'cd ~/Share/SOLARIS/ && watch -n 5 nvidia-smi'; exec bash"

# 60秒間待機
sleep 60

# ターミナル3: 左下
gnome-terminal --geometry=204x54+0+1080 -- bash -c "docker exec -it solaris02 bash -c 'cd ~/Share/SOLARIS/ && python3 RUN_monitor.py ./auto_rec.py'; exec bash"

# ターミナル4: 右下
gnome-terminal --geometry=204x54+1920+1080 -- bash -c "cd ~/Share/SOLARIS/ && python3 RUN_monitor.py /home/yuma/Share/SOLARIS/solaris_preview.py; exec bash"
