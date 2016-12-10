#!/bin/bash

p=$PWD
source ../bin/activate
touch $p/djangocron
touch $p/djangocron.log
echo "0 */6 * * * /root/ENV_PY3/bin/python $p/manage.py crawlperday > $p/djangocron.log 2>&1" >djangocron
echo "0 10 * * * /root/ENV_PY3/bin/python $p/manage.py sendemail >> $p/djangocron.log 2>&1" >> djangocron
crontab djangocron
crontab -l


