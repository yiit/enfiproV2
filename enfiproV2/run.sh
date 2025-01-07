#!/bin/bash
SCRIPT=$(readlink -f "$0")
DIR=$(dirname "$SCRIPT")
if [ -z "$DIR" ]
then
DIR=/home/pi/enfiproV2/enfiproV2
fi
cd $DIR
while true; do
python $DIR/manage.py runserver 0.0.0.0:8000
sleep 3
done