#!/bin/bash
# Determined just by echoing PATH with THI user under bash and removing "games" paths
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin:

# THIS IS RUN BY A CRONTAB!!

while getopts ":e::k:" opt; do
  case $opt in
    e) env="$OPTARG"
    ;;
    k) api_key="$OPTARG"
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
    exit 1
    ;;
  esac

  case $OPTARG in
    -*) echo "Option $opt needs a valid argument"
    exit 1
    ;;
  esac
done

if [ -z "$env" ] || [ -z "$api_key" ]
then
  echo "Please send env with -e and api key with -k"
  exit 1
fi

if [ "$env" = "prod" ];
then
  SOURCE_FILE="production.env"
else
  SOURCE_FILE="staging.env"
fi

if [ -e $SOURCE_FILE ]
  then
  echo "Found $SOURCE_FILE"
else
  echo "Could not find $SOURCE_FILE, sending error email"
  mailtext="Could not find environment to back up files on ${env}"
  bodyHTML="<p> $mailtext </p>"
  maildata='{
      "api_key": "'${api_key}'",
      "to": ["Brad Wells <brad@lovejustice.ngo>"],
      "sender": "Searchlight '${env}' Cron Alerts <system+'${env}'@lovejustice.ngo>",
      "subject": "[Searchlight -'${env}'] clone file backups cron failed",
      "html_body": "'${bodyHTML}'"
  }'
  curl --request POST \
   --url https://api.smtp2go.com/v3/email/send \
   --header 'Content-Type: application/json' \
   --data "$maildata"
   exit 1
fi

set -a
source $SOURCE_FILE
set +a

# https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-authorize-azure-active-directory
export AZCOPY_AUTO_LOGIN_TYPE="SPN"
export AZCOPY_SPA_APPLICATION_ID="$AZURE_APPLICATION_ID"
export AZCOPY_SPA_CLIENT_SECRET="$AZURE_BACKUP_CLIENT_SECRET"
export AZCOPY_TENANT_ID="$AZURE_TENANT_ID"
FILE_BACKUP_URL=https://$AZURE_BACKUP_STORAGE_ACCOUNT_NAME.blob.core.windows.net/$AZURE_FILE_BACKUP_CONTAINER/
FILE_SOURCE_URL=https://$AZURE_STORAGE_ACCOUNT_NAME.blob.core.windows.net/$AZURE_CONTAINER/

# Takes around an hour or so
# Last modified timestamps are replaced with the current time in the copy process
azcopy copy $FILE_SOURCE_URL $FILE_BACKUP_URL --recursive
# If you are testing in staging, please delete the backups that you made (probably 'staging-cloud-media' in 'searchlightdev')

AZ_COPY_STATUS=$?
if [ $AZ_COPY_STATUS -ne 0 ]
  then
  echo "Could not clone file backups, sending error email"
  mailtext="Could not clone file backups on ${env}"
  bodyHTML="<p> $mailtext </p>"
  maildata='{
      "api_key": "'${api_key}'",
      "to": ["Brad Wells <brad@lovejustice.ngo>"],
      "sender": "Searchlight '${env}' Cron Alerts <system+'${env}'@lovejustice.ngo>",
      "subject": "[Searchlight - '${env}'] clone file backups cron failed",
      "html_body": "'${bodyHTML}'"
  }'
  curl --request POST \
   --url https://api.smtp2go.com/v3/email/send \
   --header 'Content-Type: application/json' \
   --data "$maildata"
  exit 1
fi