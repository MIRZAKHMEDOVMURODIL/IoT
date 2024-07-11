#!/bin/bash

# 多重起動防止
SHNAME=$(basename "$0")
LCKNAME=/$SHNAME.lck
CURR_DIR=/IoT/bin

#履歴登録(PC起動実績)
PROC_TYPE=PC
TIME=`date "+%Y-%m-%d %H:%M:%S"`
RESULT=0
NULL=\"\"
$CURR_DIR/hist_append.sh ${PROC_TYPE} ${SHNAME} ${NULL} ${NULL} ${NULL} ${NULL} ${NULL} ${NULL} ${NULL} "${TIME}" ${RESULT} ${NULL}

if [ -e $CURR_DIR/$LCKNAME ]; then
    exit 0
fi

touch $CURR_DIR/$LCKNAME

# $CURR_DIR/smb/MountLogs.sh

$CURR_DIR/ftp/Ftp_GetLogs.sh

$CURR_DIR/date_judge.sh
if [ $? -eq 0 ]; then

$CURR_DIR/DB/DB_insert.sh

$CURR_DIR/CopyLogs.sh

$CURR_DIR/Registered_Hist.sh

fi

rm $CURR_DIR/$LCKNAME
