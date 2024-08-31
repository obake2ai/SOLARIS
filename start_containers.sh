#!/bin/bash

# Dockerコンテナを開始
docker start solaris02

# ターミナル1: 画面上部（高さの4分の1）
gnome-terminal --geometry=160x54+0+0 -- bash -c "docker exec -it solaris02 bash -c 'cd ~/Share/SOLARIS/ && python3 audio_handler.py'; exec bash"

# ターミナル2: 画面上から1/4の位置（高さの4分の1）
gnome-terminal --geometry=160x54+0+540 -- bash -c "docker exec -it solaris02 bash -c 'cd ~/Share/SOLARIS/ && watch -n 1 nvidia-smi'; exec bash"

# 60秒間待機
sleep 60

# ターミナル3: 画面上から2/4の位置（高さの4分の1）
gnome-terminal --geometry=160x54+0+1080 -- bash -c "docker exec -it solaris02 bash -c 'cd ~/Share/SOLARIS/ && python3 auto_rec.py'; exec bash"

# ターミナル4: 画面上から3/4の位置（高さの4分の1）
gnome-terminal --geometry=160x54+0+1620 -- bash -c "cd ~/Share/SOLARIS/ && python3 preview.py; exec bash"
