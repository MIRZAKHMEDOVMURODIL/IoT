#!/bin/bash

# 多重起動防止
if [ -e /IoT/ftp/ftp.sh.lck ]; then
    exit 0
fi

touch /IoT/ftp/ftp.sh.lck
cd /IoT/ftp

python3 FTPManager.py /IoT/ftp/config/FTP_FV04901_config.json
python3 FTPManager.py /IoT/ftp/config/FTP_FV04902_config.json
python3 FTPManager.py /IoT/ftp/config/FTP_FV05701_config.json

rm -f /IoT/ftp/ftp.sh.lck
