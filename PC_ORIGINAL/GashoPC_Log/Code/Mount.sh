#!/bin/bash

#バックアップするためのサーバーのフォルダ
REMOTE_SERVER="//10.21.32.90/Iotstrage/Data"

#データ連携用PCのマウントされたフォルダ
MOUNT_DIR="/IoT/PC/GashoPC_Log/Mount_Server"

# データ連携用PCのTempフォルダ内の各サブフォルダ
# FV03004_PC1_TEMP="/IoT/PC/GashoPC_Log/Temp/FV03004_PC1"  
# FV03004_PC2_TEMP="/IoT/PC/GashoPC_Log/Temp/FV03004_PC2"
FV03014_PC1_TEMP="/IoT/PC/GashoPC_Log/Temp/FV03014_PC1"  
FV03014_PC2_TEMP="/IoT/PC/GashoPC_Log/Temp/FV03014_PC2"

DIR="/IoT/PC/GashoPC_Log"
LOCK_FILE="/IoT/PC/GashoPC_Log/Code/Mount.sh.lck"

if [ -e $LOCK_FILE ]; then
    exit 0
fi

touch $LOCK_FILE
cd $DIR 


#データ連携用PCのTempフォルダ内の各サブフォルダをリモートサーバーへコピー
sudo /bin/mount -t cifs -o vers=2.0,domain='SHGCERLDS05',user='Iotusr',password='Cera1usr' $REMOTE_SERVER $MOUNT_DIR

# #FV03004_PC1_TEMPフォルダをサーバーへコピー
# sudo cp -rp -u $FV03004_PC1_TEMP $MOUNT_DIR

# #FV03004_PC2_TEMPフォルダをサーバーへコピー
# sudo cp -rp -u $FV03004_PC2_TEMP $MOUNT_DIR

#FV03014_PC1_TEMPフォルダをサーバーへコピー
sudo cp -rp -u $FV03014_PC1_TEMP $MOUNT_DIR

#FV03004_PC2_TEMPフォルダをサーバーへコピー
sudo cp -rp -u $FV03014_PC2_TEMP $MOUNT_DIR

sudo /bin/umount $MOUNT_DIR
rm -f $LOCK_FILE





