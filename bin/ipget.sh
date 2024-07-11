#!/bin/bash
TYPE=$1
if [ $TYPE = 1 ]; then
	IP=`ip addr show | grep -E '10\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' |awk '{print $2}'|cut -d"/" -f 1`
elif [ $TYPE = 2 ]; then
	IP=`ip addr show | grep -E '192\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' |awk '{print $2}'|cut -d"/" -f 1`
else
	IP=""
fi
echo -n $IP
