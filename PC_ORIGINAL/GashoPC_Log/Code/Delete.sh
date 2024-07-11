#!/bin/bash

LOCK_FILE="/IoT/PC/GashoPC_Log/Code/Delete.sh.lck"

# データ連携用PCのTemp内のサブフォルダ
FV03004_PC1="/IoT/PC/GashoPC_Log/Temp/FV03004_PC1"
FV03004_PC2="/IoT/PC/GashoPC_Log/Temp/FV03004_PC2"
FV03014_PC1="/IoT/PC/GashoPC_Log/Temp/FV03014_PC1"
FV03014_PC2="/IoT/PC/GashoPC_Log/Temp/FV03014_PC2"


if [ -e $LOCK_FILE ]; then
    exit 0
fi

touch $LOCK_FILE

#データ連携用PCのTempフォルダの各サブフォルダ内にある最終更新日が30日を超えったファイルを削除
sudo find $FV03004_PC1 -type f -mtime +30 -exec rm -f {} \;
sudo find $FV03004_PC2 -type f -mtime +30 -exec rm -f {} \;
sudo find $FV03014_PC1 -type f -mtime +30 -exec rm -f {} \;
sudo find $FV03014_PC2 -type f -mtime +30 -exec rm -f {} \;

rm -f $LOCK_FILE



