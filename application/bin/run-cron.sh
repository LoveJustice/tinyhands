#!/usr/bin/env bash

# fix folder permissions
chown -R www-data:www-data  /data
# Dump env to a file
touch /etc/cron.d/dreamsuite
env | while read line ; do
   echo "$line" >> /etc/cron.d/dreamsuite
done

# Add env vars to dreamsuite-cron to make available to scripts
cat /etc/cron.d/dreamsuite-cron >> /etc/cron.d/dreamsuite

# Remove original cron file without env vars
rm -f /etc/cron.d/dreamsuite-cron

# Start cron daemon
cron -f
