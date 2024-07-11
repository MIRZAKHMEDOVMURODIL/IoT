#!/bin/bash
echo $*
PROC_TYPE=$1
PRGM_NAME=$2
EQP_ID=$3

if [ $4 != \"\" ]
then
EQP_NAME=$4
else
EQP_NAME="MSAPシード剥離"
fi

UNIT_NUM=$5
UNIT_NAME=$6
LOG_NUM=$7
DATA_TYPE=$8
REGISTERED_TABLE=$9
REGISTERED_DT=${10}
RESULT=${11}
CONTENTS=${12}
if [ -z "${13}"]
then
MEASURED_DT=\"\"
else
MEASURED_DT=${13}
fi

#履歴登録
echo ${PROC_TYPE}","${PRGM_NAME}","${EQP_ID}","${EQP_NAME}","${UNIT_NUM}","${UNIT_NAME}","${LOG_NUM}","${DATA_TYPE}","${REGISTERED_TABLE}","${REGISTERED_DT}","${RESULT}","${CONTENTS}","${MEASURED_DT} >> /IoT/bin/hist_registered.log

