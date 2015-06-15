#!/bin/bash -x

NOW=$(date '+%F-%H-%M')
HOST=thi-production
THI_USER_HOME=~dreamsuite
OLD_PROD_PATH=$THI_USER_HOME/dreamsuite
NEW_PROD_PATH=$THI_USER_HOME/tinyhands
RSYNC='rsync --times'

# Production databases
$RSYNC $HOST:$OLD_PROD_PATH/db.sqlite3 $NOW-old-prod-db.sqlite3
$RSYNC $HOST:$NEW_PROD_PATH/db.sqlite3 $NOW-new-prod-db.sqlite3

# One offs
$RSYNC $HOST:$OLD_PROD_PATH/backup.db backup.db.sqlite3
$RSYNC $HOST:$OLD_PROD_PATH/backup-08-04-14 backup-08-04-14.sqlite3
