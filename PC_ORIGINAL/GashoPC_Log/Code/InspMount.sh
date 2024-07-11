#!/bin/bash

DIR="/IoT/PC/GashoPC_Log"
LOCK_FILE="/IoT/PC/GashoPC_Log/Code/InspMount.sh.lck"

#各画処PC側のフォルダ
FV03004_PC1_FROM="//192.168.10.100/Log/検査データログ"
FV03004_PC2_FROM="//192.168.10.101/Log/検査データログ"
FV03014_PC1_FROM="//192.168.10.102/Log/検査データログ"
FV03014_PC2_FROM="//192.168.10.103/Log/検査データログ"

# #データ連携用PCのマウントされるフォルダ
FV03004_PC1_MOUNT="/IoT/PC/GashoPC_Log/Mount_PC/FV03004_PC1" 
FV03004_PC2_MOUNT="/IoT/PC/GashoPC_Log/Mount_PC/FV03004_PC2"
FV03014_PC1_MOUNT="/IoT/PC/GashoPC_Log/Mount_PC/FV03014_PC1" 
FV03014_PC2_MOUNT="/IoT/PC/GashoPC_Log/Mount_PC/FV03014_PC2"

#データ連携用PCのTempフォルダ内のサブフォルダ
FV03004_PC1_TEMP="/IoT/PC/GashoPC_Log/Temp/FV03004_PC1"
FV03004_PC2_TEMP="/IoT/PC/GashoPC_Log/Temp/FV03004_PC2"
FV03014_PC1_TEMP="/IoT/PC/GashoPC_Log/Temp/FV03014_PC1"
FV03014_PC2_TEMP="/IoT/PC/GashoPC_Log/Temp/FV03014_PC2"


if [ -e $LOCK_FILE ]; then
    exit 0
fi

touch $LOCK_FILE
cd $DIR 


# FV03004_PC1_FROMフォルダから、過去30日以内に変更されたファイルを、データ連携用PCのFV03004_PC1_TEMPフォルダにコピー
sudo /bin/mount -t cifs -o vers=2.0,ro,domain='',user='',password='' $FV03004_PC1_FROM $FV03004_PC1_MOUNT   
sudo find $FV03004_PC1_MOUNT -type f -mtime -30 -exec cp -rp {} $FV03004_PC1_TEMP \;
sudo /bin/umount $FV03004_PC1_MOUNT


# FV03004_PC2_FROMフォルダから、過去30日以内に変更されたファイルを、データ連携用PCのFV03004_PC2_TEMPフォルダにコピー
sudo /bin/mount -t cifs -o vers=2.0,ro,domain='',user='',password='' $FV03004_PC2_FROM $FV03004_PC2_MOUNT
sudo find $FV03004_PC2_MOUNT -type f -mtime -30 -exec cp -rp {} $FV03004_PC2_TEMP \;
sudo /bin/umount $FV03004_PC2_MOUNT


# FV03014_PC1_FROMフォルダから、過去30日以内に変更されたファイルを、データ連携用PCのFV03014_PC1_TEMPフォルダにコピー
sudo /bin/mount -t cifs -o vers=2.0,ro,domain='',user='',password='' $FV03014_PC1_FROM $FV03014_PC1_MOUNT
sudo find $FV03014_PC1_MOUNT -type f -mtime -30 -exec cp -rp {} $FV03014_PC1_TEMP \;
sudo /bin/umount $FV03014_PC1_MOUNT


# FV03014_PC2_FROMフォルダから、過去30日以内に変更されたファイルを、データ連携用PCのFV03014_PC2_TEMPフォルダにコピー
sudo /bin/mount -t cifs -o vers=2.0,ro,domain='',user='',password='' $FV03014_PC2_FROM $FV03014_PC2_MOUNT
sudo find $FV03014_PC2_MOUNT -type f -mtime -30 -exec cp -rp {} $FV03014_PC2_TEMP \;
sudo /bin/umount $FV03014_PC2_MOUNT


rm -f $LOCK_FILE




# sudo /bin/umount //192.168.10.102/Log/検査データログ
# sudo /bin/mount -t cifs -o vers=2.0,ro,domain='',user='',password='' //192.168.10.102/Log/検査データログ /IoT/PC/GashoPC_Log/Mount_PC/FV03014_PC1
