#!/bin/bash
#�x�Ɗ��Ԃ̃����e�΍��p
#�w����ԓ��Ȃ�߂�l1��Ԃ�
now=`date +%s`
tm_start=`date --date "2023/08/15 06:00" +%s`
tm_end=`date --date "2023/08/15 20:00" +%s`
result=0
if [ $result -eq 1 ]; then
	result=1
elif [ $now -gt $tm_start ]; then
	if [ $now -lt $tm_end ]; then
        result=1
    fi
fi
exit ${result}
