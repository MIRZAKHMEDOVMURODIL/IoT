# 多重起動防止
if [ -e /IoT/ftp/mount.sh.lck ]; then
    exit 0
fi

touch /IoT/ftp/mount.sh.lck
cd /IoT/ftp

/bin/umount /IoT/ftp/mnt/share
/bin/mount -t cifs -o vers=2.0,domain='SHGCERLDS02',user='DBCOLL01',password='CeraColl1u' //10.21.32.70/DbStrage /IoT/ftp/mnt/share

if [ -e /IoT/ftp/mnt/share/data ]; then
    if [ ! -e /IoT/ftp/swap ]; then
        mkdir /IoT/ftp/swap
    fi
    # 更新ファイルのみコピーする
    # コピーに成功した場合のみ、tmp内のファイルをswapに移動する
    cp -r -u /IoT/ftp/tmp/FV04901 /IoT/ftp/mnt/share/data && mv -u /IoT/ftp/tmp/FV04901 /IoT/ftp/swap
    cp -r -u /IoT/ftp/tmp/FV04902 /IoT/ftp/mnt/share/data && mv -u /IoT/ftp/tmp/FV04902 /IoT/ftp/swap
    cp -r -u /IoT/ftp/tmp/FV05701 /IoT/ftp/mnt/share/data && mv -u /IoT/ftp/tmp/FV05701 /IoT/ftp/swap

    cp -R -u /IoT/ftp/tmp/FV04901_PC /IoT/ftp/mnt/share/data && mv -u /IoT/ftp/tmp/FV04901_PC /IoT/ftp/swap
    cp -R -u /IoT/ftp/tmp/FV04902_PC /IoT/ftp/mnt/share/data && mv -u /IoT/ftp/tmp/FV04902_PC /IoT/ftp/swap
    cp -R -u /IoT/ftp/tmp/FV05701_PC /IoT/ftp/mnt/share/data && mv -u /IoT/ftp/tmp/FV05701_PC /IoT/ftp/swap

    # swapの中のファイルは削除する
    if [ -e /IoT/ftp/swap ]; then
        rm -rf /IoT/ftp/swap
    fi
fi

/bin/umount /IoT/ftp/mnt/share

rm /IoT/ftp/mount.sh.lck
