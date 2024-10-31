#!/bin/bash
count=`cat /app/zbx-script/count.txt`
count=$((count-1))
echo $count
echo $count > /app/zbx-script/count.txt