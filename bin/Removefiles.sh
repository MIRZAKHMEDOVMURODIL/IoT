#!/bin/bash

# 多重起動防止
if [ -e /IoT/bin/remove.sh.lck ]; then
    exit 0
fi

touch /IoT/bin/remove.sh.lck
cd /IoT/bin/

rm -rf /IoT/bin/swap && mkdir /IoT/bin/swap
chown admin.admin /IoT/bin/swap
rm /IoT/bin/remove.sh.lck
