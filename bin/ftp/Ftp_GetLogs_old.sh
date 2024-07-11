#!/bin/bash

CURR_DIR=/IoT/bin/ftp
PYSCRIPT=$CURR_DIR/FTPManager.py
SHNAME=$(basename "$0")
CONFIG_DIR=$CURR_DIR/config

#履歴登録(FTP操作実績)
PROC_TYPE=FTP
TIME=`date "+%Y-%m-%d %H:%M:%S"`
RESULT=0
NULL=\"\"
/IoT/bin/hist_append.sh ${PROC_TYPE} ${SHNAME} ${NULL} ${NULL} ${NULL} ${NULL} ${NULL} ${NULL} ${NULL} "${TIME}" ${RESULT} ${NULL}

cd $CURR_DIR

# 多重起動防止
LCKNAME=/$SHNAME.lck
if [ -e $CURR_DIR/$LCKNAME ]; then
    exit 0
fi

touch $CURR_DIR/$LCKNAME

python3 /IoT/bin/ftp/FTPManager.py /IoT/bin/ftp/config/000/STS.json

python3 /IoT/bin/ftp/FTPManager.py /IoT/bin/ftp/config/010/ALM.json
python3 /IoT/bin/ftp/FTPManager.py /IoT/bin/ftp/config/010/STS.json
python3 /IoT/bin/ftp/FTPManager.py /IoT/bin/ftp/config/010/STS_raw.json

python3 /IoT/bin/ftp/FTPManager.py /IoT/bin/ftp/config/020/ALM.json
python3 /IoT/bin/ftp/FTPManager.py /IoT/bin/ftp/config/020/STS.json
python3 /IoT/bin/ftp/FTPManager.py /IoT/bin/ftp/config/020/STS_raw.json
python3 /IoT/bin/ftp/FTPManager.py /IoT/bin/ftp/config/020/QC_log1.json
python3 /IoT/bin/ftp/FTPManager.py /IoT/bin/ftp/config/020/QC_log2.json
python3 /IoT/bin/ftp/FTPManager.py /IoT/bin/ftp/config/020/TS_log1.json

python3 /IoT/bin/ftp/FTPManager.py /IoT/bin/ftp/config/030/ALM.json
python3 /IoT/bin/ftp/FTPManager.py /IoT/bin/ftp/config/030/STS.json
python3 /IoT/bin/ftp/FTPManager.py /IoT/bin/ftp/config/030/STS_raw.json
python3 /IoT/bin/ftp/FTPManager.py /IoT/bin/ftp/config/030/COUNT.json

rm -f $CURR_DIR/$LCKNAME
