#!/bin/bash

set -x

## rsync select files from the THI production server.

## Notes on rsync flags
## --delete (delete extraneous files on receiving side) -- DON'T DO THIS
## --archive == -rlptgoD
##  --recursive (recurse into directories)
##  --links     (copy symlinks as symlinks)
##  --perms     (preserve permissions)
##  --times     (preserve modification times)
##  --group     (preserve group)
##  --owner     (preserve owner)
##  --devices   (-D => preserve device files - SU only)
##  --specials  (-D => preserve special files)

RS='mkdir --parents'
YEAR=$(date '+%Y')
MONTH=$(date '+%B')
NEW_DIR=backups/$YEAR/$MONTH

RSYNC='rsync --verbose --archive --progress --rsh=ssh'
#THI_PROD='thi-production:/home/dreamsuite/dreamsuite'
THI_PROD='thi-production:/home/dreamsuite/tinyhands'

NOW=$(date '+%F-%H-%M')

$DIRS $NEW_DIR

$RSYNC $THI_PROD/db.sqlite3 backups/$NEW_DIR/db-$NOW.sqlite3
$RSYNC $THI_PROD/media .
