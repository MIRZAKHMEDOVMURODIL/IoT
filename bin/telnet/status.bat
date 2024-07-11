#!/bin/bash

WDIR="/IoT/bin/telnet"
CMDNAME="status"
PSCRIPT="status.py"
PYTHON_BIN="python3"
M_NAME="$2"
ARGFILE="tmp_${CMDNAME}_${M_NAME}_arg.txt"
DATE=`date "+%Y%m%d"`
LOGFILE="log/${CMDNAME}_${M_NAME}_${DATE}.log"

cd ${WDIR}

echo -n '' > ${ARGFILE}
for arg in "$@"; do
  echo ${arg} >> ${ARGFILE}
done

${PYTHON_BIN} ${PSCRIPT} ${ARGFILE} &>> ${LOGFILE}

# rm ${ARGFILE}
