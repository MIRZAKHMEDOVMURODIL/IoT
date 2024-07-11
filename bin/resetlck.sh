#!/bin/bash

##############################################
# dirpath以下のサブディレクトリ含めてlckファイルを検索、削除を実行
# (実行はcrontabのrebootで実行)
##############################################
dirpath=/IoT/bin
for file in `find ${dirpath} -type f -name '*.lck'`
do
  rm ${file}
done

