#!/bin/bash

if [ $# != 1 ];then
echo "Invalid command: $1"
echo "Usage: $0 {start|stop}"
exit 1
fi
echo $1
if [ $1 = 'start' ]; then
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8080 --timeout-keep-alive 300 --proxy-headers --reload &
elif [ $1 = 'stop' ]; then
    ps uxa | grep 'uvicorn app.main:app' | grep -v  grep | awk '{print $2}' | xargs kill -9
    lsof -i:8080 | grep 8080 | awk '{print $2}' | xargs kill -9
else
  echo "Invalid command: $1"
  echo "Usage: $0 {start|stop}"
  exit 1
fi
