#!/bin/bash

# 多重起動防止
if [ -e /IoT/bin/DB/DB_insert.lck ]; then
    exit 0
fi

touch /IoT/bin/DB/DB_insert.lck 

#DB2環境変数設定
cd /IoT/db2driver/dsdriver
. ./db2profile

#　PC設備のデータをDBへ書き込む
cd /IoT/bin/DB

# 000(ライン稼働率)
python3 /IoT/bin/DB/db2_STS.py /IoT/bin/DB/config/000/STS.json

# 010
python3 /IoT/bin/DB/db2_ALM.py /IoT/bin/DB/config/010/ALM.json
python3 /IoT/bin/DB/db2_STS.py /IoT/bin/DB/config/010/STS.json
python3 /IoT/bin/DB/db2_STS_raw.py /IoT/bin/DB/config/010/STS_raw.json

# 020
python3 /IoT/bin/DB/db2_STS.py /IoT/bin/DB/config/020/STS.json
python3 /IoT/bin/DB/db2_STS_raw.py /IoT/bin/DB/config/020/STS_raw.json
python3 /IoT/bin/DB/db2_TS_new.py /IoT/bin/DB/config/020/log1_TS.json
python3 /IoT/bin/DB/db2_QC.py /IoT/bin/DB/config/020/log1_QC.json
python3 /IoT/bin/DB/db2_QC.py /IoT/bin/DB/config/020/log2_QC.json
python3 /IoT/bin/DB/db2_ALM.py /IoT/bin/DB/config/020/ALM.json

# 030
python3 /IoT/bin/DB/db2_ALM.py /IoT/bin/DB/config/030/ALM.json
python3 /IoT/bin/DB/db2_STS.py /IoT/bin/DB/config/030/STS.json
python3 /IoT/bin/DB/db2_STS_raw.py /IoT/bin/DB/config/030/STS_raw.json
python3 /IoT/bin/DB/db2_COUNT.py /IoT/bin/DB/config/030/COUNT.json

rm /IoT/bin/DB/DB_insert.lck