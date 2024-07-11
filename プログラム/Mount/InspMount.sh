# 多重起動防止
if [ -e /IoT/ftp/insp.sh.lck ]; then
    exit 0
fi


touch /IoT/ftp/insp.sh.lck
cd /IoT/ftp


/bin/mount -t cifs -o vers=2.0,ro,user=visionsystem,password='',iocharset=utf8,uid=1002,gid=1002 //192.168.10.100/lotinfo_inspdatalog /IoT/ftp/mnt/FV04901_PC/LotInfo_InspDataLog
cp -r -u /IoT/ftp/mnt/FV04901_PC/LotInfo_InspDataLog /IoT/ftp/tmp/FV04901_PC/
/bin/umount /IoT/ftp/mnt/FV04901_PC/LotInfo_InspDataLog


rm /IoT/ftp/insp.sh.lck



