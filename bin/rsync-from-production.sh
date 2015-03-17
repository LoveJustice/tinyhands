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

RSYNC='rsync --verbose --archive --progress --rsh=ssh'
THI_PROD='thi-production:/home/dreamsuite/dreamsuite'

$RSYNC $THI_PROD/db.sqlite3 db.sqlite3.prod
$RSYNC $THI_PROD/media .
