#!/bin/bash

# 多重起動防止
SHNAME=$(basename "$0")
LCKNAME=/$SHNAME.lck
CURR_DIR=/IoT/bin

if [ -e $CURR_DIR/$LCKNAME ]; then
    exit 0
fi

touch $CURR_DIR/$LCKNAME

# cd $CURR_DIR

rm -f $CURR_DIR/hist.log

# rm -f $CURR_DIR/ftp/log/debug.log && touch $CURR_DIR/ftp/log/debug.log
find $CURR_DIR/ftp/log/*.log -mtime +14 -exec rm -f {} \;

# rm -f $CURR_DIR/DB/debug.log && touch $CURR_DIR/DB/debug.log
find $CURR_DIR/DB/log/*.log -mtime +14 -exec rm -f {} \;

rm $CURR_DIR/$LCKNAME
