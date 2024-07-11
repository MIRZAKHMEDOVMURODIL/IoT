#!/bin/bash

LOCK_FILE="/IoT/PC/EQP_Log/Code/Get_Data.sh.lck"
SCRIPT_DIR="/IoT/PC/EQP_Log/Code"

if [ -e $LOCK_FILE ]; then
    exit 0
fi

touch $LOCK_FILE
cd $SCRIPT_DIR


#FTPを用いてTPに接続し、データ連携用PCのTempフォルダのFV03004フォルダにデータを取得します。
python3 /IoT/PC/EQP_Log/Code/FTPManager.py /IoT/PC/EQP_Log/Code/Config/FTP_FV03004.json

#FTPを用いてTPに接続し、データ連携用PCのTempフォルダのFV03014フォルダにデータを取得します。
python3 /IoT/PC/EQP_Log/Code/FTPManager.py /IoT/PC/EQP_Log/Code/Config/FTP_FV03014.json

rm -f $LOCK_FILE


