# 多重起動防止
if [ -e /home/iot/ftp/remove.sh.lck ]; then
    exit 0
fi

touch /home/iot/ftp/remove.sh.lck
cd /home/iot/ftp

if [ -e /home/iot/ftp/swap ]; then
    rm -rf /home/iot/ftp/swap
fi
rm /home/iot/ftp/remove.sh.lck
