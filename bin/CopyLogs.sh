#!/bin/bash

# 多重起動防止
SHNAME=$(basename "$0")
LCKNAME=/$SHNAME.lck
CURR_DIR=/IoT/bin

#履歴登録(NAS操作実績)
PROC_TYPE=NAS
TIME=`date "+%Y-%m-%d %H:%M:%S"`
RESULT=0
NULL=\"\"
/IoT/bin/hist_append.sh ${PROC_TYPE} ${SHNAME} ${NULL} ${NULL} ${NULL} ${NULL} ${NULL} ${NULL} ${NULL} "${TIME}" ${RESULT} ${NULL}

if [ -e $CURR_DIR/$LCKNAME ]; then
    exit 0
fi

touch $CURR_DIR/$LCKNAME

cd $CURR_DIR

# NAS　umount確認
sudo /bin/umount /IoT/bin/nas
#NAS
sudo /bin/mount -t cifs -o vers=2.0,domain='AD',user='Ayabe3user',password='Zaq12wsx' //10.143.16.193/01_Data/Bldg3/B22_LEV50001 /IoT/bin/nas


# データ収集対象 tmp/ -> nas
# A && B：Aが成功したらBを実行
# 　option : -r ディレクトリ　　-u タイムスタンプが新しいファイルのみコピー
#PLC設備　----→　NAS
sudo cp -r -u /IoT/bin/ftp/tmp/000 /IoT/bin/nas && cp -r -u /IoT/bin/ftp/tmp/000 /IoT/bin/swap && rm -r /IoT/bin/ftp/tmp/000/*
sudo cp -r -u /IoT/bin/ftp/tmp/010 /IoT/bin/nas && cp -r -u /IoT/bin/ftp/tmp/010 /IoT/bin/swap && rm -r /IoT/bin/ftp/tmp/010/*
sudo cp -r -u /IoT/bin/ftp/tmp/020 /IoT/bin/nas && cp -r -u /IoT/bin/ftp/tmp/020 /IoT/bin/swap && rm -r /IoT/bin/ftp/tmp/020/*
sudo cp -r -u /IoT/bin/ftp/tmp/030 /IoT/bin/nas && cp -r -u /IoT/bin/ftp/tmp/030 /IoT/bin/swap && rm -r /IoT/bin/ftp/tmp/030/*


#umount
sudo /bin/umount /IoT/bin/nas
# ロックファイル削除
rm $CURR_DIR/$LCKNAME