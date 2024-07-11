# 多重起動防止
if [ -e /IoT/ftp/insp.sh.lck ]; then
    exit 0
fi

touch /IoT/ftp/insp.sh.lck
cd /IoT/ftp

# FV04901(画像検査1号機)
#LotInfo_InspDataLog(検査DATA)
/bin/mount -t cifs -o vers=2.0,ro,user=visionsystem,password='',iocharset=utf8,uid=1002,gid=1002 //192.168.10.100/lotinfo_inspdatalog /IoT/ftp/mnt/FV04901_PC/LotInfo_InspDataLog
cp -R -u /IoT/ftp/mnt/FV04901_PC/LotInfo_InspDataLog /IoT/ftp/tmp/FV04901_PC/
/bin/umount /IoT/ftp/mnt/FV04901_PC/LotInfo_InspDataLog

#FTP_user
/bin/mount -t cifs -o vers=2.0,ro,user=visionsystem,password='',iocharset=utf8,uid=1002,gid=1002 //192.168.10.100/FTP_user/FTP_user /IoT/ftp/mnt/FV04901_PC/FTP_user
cp -R -u /IoT/ftp/mnt/FV04901_PC/FTP_user /IoT/ftp/tmp/FV04901_PC/
/bin/umount /IoT/ftp/mnt/FV04901_PC/FTP_user

#Daily_Report
/bin/mount -t cifs -o vers=2.0,ro,user=visionsystem,password='',iocharset=utf8,uid=1002,gid=1002 //192.168.10.100/Daily_report /IoT/ftp/mnt/FV04901_PC/Daily_Report
cp -R -u /IoT/ftp/mnt/FV04901_PC/Daily_Report /IoT/ftp/tmp/FV04901_PC/
/bin/umount /IoT/ftp/mnt/FV04901_PC/Daily_Report

# # FV04902(画像検査2号機)
#LotInfo_InspDataLog(検査DATA)
/bin/mount -t cifs -o vers=2.0,ro,user=visionsystem,password='',iocharset=utf8,uid=1002,gid=1002 //192.168.10.101/lotinfo_inspdatalog /IoT/ftp/mnt/FV04902_PC/LotInfo_InspDataLog
cp -R -u /IoT/ftp/mnt/FV04902_PC/LotInfo_InspDataLog /IoT/ftp/tmp/FV04902_PC/
/bin/umount /IoT/ftp/mnt/FV04902_PC/LotInfo_InspDataLog

#FTP_user
/bin/mount -t cifs -o vers=2.0,ro,user=visionsystem,password='',iocharset=utf8,uid=1002,gid=1002 //192.168.10.101/FTP_user/FTP_user /IoT/ftp/mnt/FV04902_PC/FTP_user
cp -R -u /IoT/ftp/mnt/FV04902_PC/FTP_user /IoT/ftp/tmp/FV04902_PC/
/bin/umount /IoT/ftp/mnt/FV04902_PC/FTP_user

#Daily_Report
/bin/mount -t cifs -o vers=2.0,ro,user=visionsystem,password='',iocharset=utf8,uid=1002,gid=1002 //192.168.10.101/Daily_report /IoT/ftp/mnt/FV04902_PC/Daily_Report
cp -R -u /IoT/ftp/mnt/FV04902_PC/Daily_Report /IoT/ftp/tmp/FV04902_PC/
/bin/umount /IoT/ftp/mnt/FV04902_PC/Daily_Report

# # FV05701(画像検査3号機)
#LotInfo_InspDataLog(検査DATA)
/bin/mount -t cifs -o vers=2.0,ro,user=visionsystem,password='',iocharset=utf8,uid=1002,gid=1002 //192.168.10.102/lotinfo_inspdatalog /IoT/ftp/mnt/FV05701_PC/LotInfo_InspDataLog
cp -R -u /IoT/ftp/mnt/FV05701_PC/LotInfo_InspDataLog /IoT/ftp/tmp/FV05701_PC/
/bin/umount /IoT/ftp/mnt/FV05701_PC/LotInfo_InspDataLog

#Daily_Report
/bin/mount -t cifs -o vers=2.0,ro,user=visionsystem,password='',iocharset=utf8,uid=1002,gid=1002 //192.168.10.102/Daily_report /IoT/ftp/mnt/FV05701_PC/Daily_Report
cp -R -u /IoT/ftp/mnt/FV05701_PC/Daily_Report /IoT/ftp/tmp/FV05701_PC/
/bin/umount /IoT/ftp/mnt/FV05701_PC/Daily_Report

rm /IoT/ftp/insp.sh.lck
