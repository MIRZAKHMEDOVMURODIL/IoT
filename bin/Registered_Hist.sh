#!/bin/bash

# 多重起動防止
SHNAME=$(basename "$0")
LCKNAME=/$SHNAME.lck
CURR_DIR=/IoT/bin

if [ -e $CURR_DIR/$LCKNAME ]; then
    exit 0
fi

touch $CURR_DIR/$LCKNAME

#DB2環境変数設定
cd /IoT/db2driver/dsdriver
. ./db2profile

#履歴登録
python3 /IoT/bin/Registered_Hist.py /IoT/bin/common.jsonc

rm $CURR_DIR/$LCKNAME