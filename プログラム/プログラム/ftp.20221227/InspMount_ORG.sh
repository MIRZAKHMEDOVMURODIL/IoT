# 多重起動防止
if [ -e /IoT/ftp/insp.sh.lck ]; then
    exit 0
fi

touch /IoT/ftp/insp.sh.lck
cd /IoT/ftp

# FV04901(画像検査1号機)
/bin/mount -t cifs -o vers=2.0,ro,user=visionsystem,password='',iocharset=utf8,uid=1002,gid=1002 //192.168.10.100/lotinfo_inspdatalog /IoT/ftp/mnt/FV04901_PC
cp -R -u /IoT/ftp/mnt/FV04901_PC /IoT/ftp/tmp/
/bin/umount /IoT/ftp/mnt/FV04901_PC

# # FV04902(画像検査2号機)
/bin/mount -t cifs -o vers=2.0,ro,user=visionsystem,password='',iocharset=utf8,uid=1002,gid=1002 //192.168.10.101/lotinfo_inspdatalog /IoT/ftp/mnt/FV04902_PC
cp -R -u /IoT/ftp/mnt/FV04902_PC /IoT/ftp/tmp/
/bin/umount /IoT/ftp/mnt/FV04902_PC

# # FV04902(画像検査3号機)
/bin/mount -t cifs -o vers=2.0,ro,user=visionsystem,password='',iocharset=utf8,uid=1002,gid=1002 //192.168.10.102/lotinfo_inspdatalog /IoT/ftp/mnt/FV05701_PC
cp -R -u /IoT/ftp/mnt/FV05701_PC /IoT/ftp/tmp/
/bin/umount /IoT/ftp/mnt/FV05701_PC

rm /IoT/ftp/insp.sh.lck
