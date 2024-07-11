#!/bin/bash

WDIR="/IoT/bin"
CMDNAME="syuno"
PSCRIPT="syuno.py"
PYTHON_BIN="/usr/bin/python3"
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
