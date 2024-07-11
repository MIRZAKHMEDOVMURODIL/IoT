#!/bin/bash
cd /IoT/bin/telnet/log
find ./*.log -mtime +15 -exec rm -f {} \;