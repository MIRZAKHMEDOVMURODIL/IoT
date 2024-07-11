#!/bin/bash

CURR_DIR=/IoT/bin/DB
PY_STS=$CURR_DIR/db2_STS_r1.py
PY_STS_RAW=$CURR_DIR/db2_STS_raw_r1.py
PY_ALM=$CURR_DIR/db2_ALM_r1.py
PY_QC=$CURR_DIR/db2_QC_r1.py
PY_TS=$CURR_DIR/db2_TS_r1.py
PY_COUNT=$CURR_DIR/db2_COUNT_r1.py
PY_HOKYU=$CURR_DIR/db2_hokyu_r1.py
SHNAME=$(basename "$0")
LCKNAME=/$SHNAME.lck
CONFIG_DIR=$CURR_DIR/config

#履歴登録(DB登録開始)
PROC_TYPE=DB
TIME=`date "+%Y-%m-%d %H:%M:%S"`
RESULT=0
NULL=\"\"
/IoT/bin/hist_append.sh ${PROC_TYPE} ${SHNAME} ${NULL} ${NULL} ${NULL} ${NULL} ${NULL} ${NULL} ${NULL} "${TIME}" ${RESULT} ${NULL}

# 多重起動防止
if [ -e $CURR_DIR/$LCKNAME ]; then
    exit 0
fi

touch $CURR_DIR/$LCKNAME

# 000(ライン稼働率)
python3 /IoT/bin/DB/db2_STS.py /IoT/bin/DB/config/000/STS.json

# 010
python3 /IoT/bin/DB/db2_ALM.py /IoT/bin/DB/config/010/ALM.json
python3 /IoT/bin/DB/db2_STS.py /IoT/bin/DB/config/010/STS.json
python3 /IoT/bin/DB/db2_STS_raw.py /IoT/bin/DB/config/010/STS_raw.json

# 020
python3 /IoT/bin/DB/db2_STS.py /IoT/bin/DB/config/020/STS.json
python3 /IoT/bin/DB/db2_STS_raw.py /IoT/bin/DB/config/020/STS_raw.json
python3 /IoT/bin/DB/db2_TS.py /IoT/bin/DB/config/020/log1_TS.json
python3 /IoT/bin/DB/db2_QC.py /IoT/bin/DB/config/020/log1_QC.json
python3 /IoT/bin/DB/db2_QC.py /IoT/bin/DB/config/020/log2_QC.json
python3 /IoT/bin/DB/db2_ALM.py /IoT/bin/DB/config/020/ALM.json

# 030
python3 /IoT/bin/DB/db2_ALM.py /IoT/bin/DB/config/030/ALM.json
python3 /IoT/bin/DB/db2_STS.py /IoT/bin/DB/config/030/STS.json
python3 /IoT/bin/DB/db2_STS_raw.py /IoT/bin/DB/config/030/STS_raw.json
python3 /IoT/bin/DB/db2_COUNT.py /IoT/bin/DB/config/030/COUNT.json

rm $CURR_DIR/$LCKNAME