#!/bin/bash

p=$PWD
touch $p/djangocron
touch $p/djangocron.log
echo "0 /3 * * * python3 $p/manage.py crawlperday > $p/djangocron.log 2>&1" >djangocron
echo "0 18 * * * python3 $p/manage.py sendemail >> $p/djangocron.log 2>&1" >> djangocron
crontab djangocron
crontab -l

