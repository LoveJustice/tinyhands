#!/usr/bin/env bash

# fix folder permissions
chown -R www-data:www-data \
  /data/console/runtime/ \
  /data/frontend/runtime/ \
  /data/frontend/web/assets/

# Dump env to a file
touch /etc/cron.d/doorman
env | while read line ; do
   echo "$line" >> /etc/cron.d/doorman
done

# Add env vars to doorman-cron to make available to scripts
cat /etc/cron.d/doorman-cron >> /etc/cron.d/doorman

# Remove original cron file without env vars
rm -f /etc/cron.d/doorman-cron

# Start cron daemon
cron -f
