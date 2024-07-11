#!/bin/bash

# 多重起動防止
if [ -e /home/admin/デスクトップ/IoT/Code/mount.sh.lck ]; then
    exit 0
fi

touch /home/admin/デスクトップ/IoT/Code/mount.sh.lck

cd /home/admin/デスクトップ/IoT

/bin/umount /IoT/ftp/mnt/share
/bin/mount -t cifs -o vers=2.0,domain='AD',user='00220401626',password='Mm3001645$' //10.37.152.184/Server /home/admin/デスクトップ/IoT/Temp

if [ -e /home/admin/デスクトップ/IoT/share/data ]; then
    if [ ! -e /home/admin/デスクトップ/IoT/swap ]; then
        mkdir /IoT/ftp/swap
    fi
  
    cp -r -u /IoT/ftp/tmp/FV04901 /IoT/ftp/mnt/share/data && mv -u /IoT/ftp/tmp/FV04901 /IoT/ftp/swap

    if [ -e /IoT/ftp/swap ]; then
        rm -rf /IoT/ftp/swap
    fi
fi


/bin/umount /IoT/ftp/mnt/share

rm -f /IoT/ftp/mount.sh.lck




