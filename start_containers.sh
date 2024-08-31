#!/bin/bash

# Dockerコンテナを開始
docker start solaris02

gnome-terminal -- bash -c "docker exec -it solaris02 bash -c 'cd ~/Share/SOLARIS/ && python3 audio_handler.py'; exec bash"
gnome-terminal -- bash -c "docker exec -it solaris02 bash -c 'cd ~/Share/SOLARIS/ && watch -n 1 nvidia-smi'; exec bash"

sleep 60

gnome-terminal -- bash -c "docker exec -it solaris02 bash -c 'cd ~/Share/SOLARIS/ && python3 auto_rec.py'; exec bash"
gnome-terminal -- bash -c "docker exec -it solaris02 bash -c 'cd ~/Share/SOLARIS/ && python3 preview.py'; exec bash"
