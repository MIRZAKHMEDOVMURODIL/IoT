#!/bin/bash
LOCK_FILE="/IoT/PC/EQP_Log/Code/Delete.sh.lck"

# データ連携用PCのTempフォルダのサブフォルダ
FV03004="/IoT/PC/EQP_Log/Temp/FV03004"
FV03014="/IoT/PC/EQP_Log/Temp/FV03014"

if [ -e $LOCK_FILE ]; then
    exit 0
fi

touch $LOCK_FILE

#データ連携用PCのTempフォルダの各サブフォルダ内にある最終更新日が30日を超えったファイルを削除
sudo find $FV03004 -type f -mtime +30 -exec rm -f {} \;
sudo find $FV03014 -type f -mtime +30 -exec rm -f {} \;

rm -f $LOCK_FILE





