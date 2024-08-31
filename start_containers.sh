#!/bin/bash

# Dockerコンテナを開始
docker start solaris02

# ターミナル1: 左上
gnome-terminal --geometry=160x54+0+0 -- bash -c "docker exec -it solaris02 bash -c 'cd ~/Share/SOLARIS/ && python3 audio_handler.py'; exec bash"

# ターミナル2: 右上
gnome-terminal --geometry=160x54+1920+0 -- bash -c "docker exec -it solaris02 bash -c 'cd ~/Share/SOLARIS/ && watch -n 1 nvidia-smi'; exec bash"

# 60秒間待機
sleep 60

# ターミナル3: 左下
gnome-terminal --geometry=160x54+0+1080 -- bash -c "docker exec -it solaris02 bash -c 'cd ~/Share/SOLARIS/ && python3 auto_rec.py'; exec bash"

# ターミナル4: 右下
gnome-terminal --geometry=160x54+1920+1080 -- bash -c "cd ~/Share/SOLARIS/ && python3 preview.py; exec bash"
