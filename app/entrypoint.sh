#!/bin/bash
cp /usr/share/zoneinfo/America/Mexico_City /etc/localtime
echo "America/Mexico_City" > /etc/timezone
apk del tzdata
echo "*/35 16 * * * python3 /app/sslcheck.py >> ~/cron.log 2>&1" > crontab.tmp
crontab crontab.tmp
crond start
python ./api.py