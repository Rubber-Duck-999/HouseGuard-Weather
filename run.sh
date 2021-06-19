#!/bin/sh

echo '~ Checking all things'

if git pull;
then
    echo 'Pass'
else
    echo 'Fail to grab'
fi

if [ -f "/home/pi/Documents/runtime.log" ];
then
    rm /home/pi/Documents/runtime.log
else
    touch /home/pi/Documents/runtime.log
fi

cd /home/pi/Documents/weather/

python3 main.py