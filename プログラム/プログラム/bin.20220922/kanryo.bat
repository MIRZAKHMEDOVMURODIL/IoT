#!/bin/bash

WORK_DIR="/IoT/bin"
CMDNAME="kanryo"
PSCRIPT="kanryo.py"
M_NAME="$5"

ARGFILE="tmp_${CMDNAME}_${M_NAME}_arg.txt"
LOG_PRE="${CMDNAME}_${M_NAME}"

cd ${WORK_DIR}
echo -n '' > ${ARGFILE}
for arg in "$@"; do
  echo ${arg} >> ${ARGFILE}
done
/usr/bin/python3 ${PSCRIPT} ${ARGFILE} &>> log/${LOG_PRE}.log
rm ${ARGFILE}
tail -n 5000 log/${LOG_PRE}.log > log/tmp_${LOG_PRE}.log
mv log/tmp_${LOG_PRE}.log log/${LOG_PRE}.log
