#!/bin/bash -x

# Take a database snapshot from the old and new production instances and the staging
# instance.

# Time and date stamp
NOW=$(date '+%F-%H-%M')

PROD_HOST=thi-production
PROD_HOME=~dreamsuite
PROD_NEW_PATH=$PROD_HOST:$PROD_HOME/tinyhands
PROD_OLD_PATH=$PROD_HOST:$PROD_HOME/dreamsuite

STAGING_HOST=thi.cse.taylor.edu%proxy
STAGING_HOME=~thi
STAGING_PATH=$STAGING_HOST:$STAGING_HOME/tinyhands

RSYNC='rsync --progress --times'

$RSYNC $PROD_OLD_PATH/db.sqlite3 prod-old/db-$NOW.sqlite3
$RSYNC $PROD_NEW_PATH/db.sqlite3 prod-new/db-$NOW.sqlite3
$RSYNC $STAGING_PATH/db.sqlite3 staging/db-$NOW.sqlite3
