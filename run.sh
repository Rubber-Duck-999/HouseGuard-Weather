#!/bin/sh

echo '~ Checking all things'

if git pull;
then
    echo 'Pass'
else
    echo 'Fail to grab'
fi

export server_address="http://192.168.0.38:5000/weather"