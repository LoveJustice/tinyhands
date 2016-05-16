#!/bin/bash

set -x

RS='mkdir --parents'

RSYNC='rsync --verbose --archive --progress --rsh=ssh'

THI_PROD_MEDIA='thi-production:/home/thi/tinyhands/media'
PROJECT_DIR='/data/'

$RSYNC $THI_PROD_MEDIA $PROJECT_DIR
