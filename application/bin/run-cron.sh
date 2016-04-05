#!/usr/bin/env bash

# fix folder permissions
# Dump env to a file
touch /etc/cron.d/dreamsuite-env
env | while read line ; do
   echo "$line" >> /etc/cron.d/dreamsuite-env
done

# Add env vars to dreamsuite-cron to make available to scripts
cat /etc/cron.d/dreamsuite-env >> /etc/cron.d/tinyhands-cron

# Remove original cron file without env vars
rm -f /etc/cron.d/dreamsuite-env

# Start cron daemon
cron -f
