#!/bin/bash

# Dockerコンテナを開始
docker start solaris02

# ターミナル1: docker exec -it solaris02 nvidia-smi
gnome-terminal -- bash -c "docker exec -it solaris02 nvidia-smi; exec bash"

# ターミナル2: docker exec -it solaris02 ls
gnome-terminal -- bash -c "docker exec -it solaris02 ls; exec bash"

# ターミナル3: docker exec -it solaris02 pwd
gnome-terminal -- bash -c "docker exec -it solaris02 pwd; exec bash"

# ターミナル4: docker exec -it solaris02 du
gnome-terminal -- bash -c "docker exec -it solaris02 watch -n 1 nvidia-smi; exec bash"
