#!/bin/bash

# ログファイルの場所
LOGFILE="$HOME/startup_script.log"

# ログファイルの開始メッセージ
echo "Starting script..." > $LOGFILE

# DISPLAY環境変数の設定
export DISPLAY=:0
echo "DISPLAY set to $DISPLAY" >> $LOGFILE

# Dockerコンテナの存在確認と起動
if [ "$(docker ps -q -f name=solaris02)" ]; then
    echo "solaris is already running." >> $LOGFILE
else
    echo "solaris is opening..." >> $LOGFILE
    docker start solaris02 >> $LOGFILE 2>&1
fi

# 画面の解像度を取得
SCREEN_RESOLUTION=$(xrandr | grep '*' | awk '{print $1}')
SCREEN_WIDTH=$(echo $SCREEN_RESOLUTION | cut -d'x' -f1)
SCREEN_HEIGHT=$(echo $SCREEN_RESOLUTION | cut -d'x' -f2)

# ログに画面の解像度を記録
echo "Screen resolution: ${SCREEN_WIDTH}x${SCREEN_HEIGHT}" >> $LOGFILE

# ターミナルウィンドウのサイズと位置を計算
TERM_WIDTH=$((SCREEN_WIDTH / 4))
TERM_HEIGHT=$((SCREEN_HEIGHT / 4))
echo "Terminal width: ${TERM_WIDTH}, Terminal height: ${TERM_HEIGHT}" >> $LOGFILE

# ターミナル1: 左上
gnome-terminal --geometry=${TERM_WIDTH}x${TERM_HEIGHT}+0+0 -- bash -c "docker exec -it solaris02 bash -c 'cd ~/Share/SOLARIS/ && python3 RUN_monitor.py ./audio_handler.py'; exec bash" >> $LOGFILE 2>&1

# ターミナル2: 右上
gnome-terminal --geometry=${TERM_WIDTH}x${TERM_HEIGHT}+$((SCREEN_WIDTH - TERM_WIDTH))+0 -- bash -c "docker exec -it solaris02 bash -c 'cd ~/Share/SOLARIS/ && watch -n 5 nvidia-smi'; exec bash" >> $LOGFILE 2>&1

# 60秒間待機
echo "Sleeping for 60 seconds..." >> $LOGFILE
sleep 60

# ターミナル3: 左下
gnome-terminal --geometry=${TERM_WIDTH}x${TERM_HEIGHT}+0+$((SCREEN_HEIGHT - TERM_HEIGHT)) -- bash -c "docker exec -it solaris02 bash -c 'cd ~/Share/SOLARIS/ && python3 RUN_monitor.py ./auto_rec.py'; exec bash" >> $LOGFILE 2>&1

# ターミナル4: 右下
gnome-terminal --geometry=${TERM_WIDTH}x${TERM_HEIGHT}+$((SCREEN_WIDTH - TERM_WIDTH))+$((SCREEN_HEIGHT - TERM_HEIGHT)) -- bash -c "cd ~/Share/SOLARIS/ && python3 RUN_monitor.py /home/yuma/Share/SOLARIS/solaris_preview.py; exec bash" >> $LOGFILE 2>&1

# スクリプト終了のログ
echo "Script finished." >> $LOGFILE
