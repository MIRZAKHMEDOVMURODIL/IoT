#!/bin/bash

##############################################
# dirpath�ȉ��̃T�u�f�B���N�g���܂߂�lck�t�@�C���������A�폜�����s
# (���s��crontab��reboot�Ŏ��s)
##############################################
dirpath=/IoT/bin
for file in `find ${dirpath} -type f -name '*.lck'`
do
  rm ${file}
done

