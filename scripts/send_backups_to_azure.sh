# THIS IS RUN BY A CRONTAB!!
# MUST BE RUN WITH THI USER

# Assumes remote has bash... https://unix.stackexchange.com/a/129401
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
  mailtext="Could not find environment to send DB backups on ${env}"
  bodyHTML="<p> $mailtext </p>"
  maildata='{
      "api_key": "'${api_key}'",
      "to": ["Brad Wells <brad@lovejustice.ngo>"],
      "sender": "Searchlight '${env}' Cron Alerts <system+'${env}'@lovejustice.ngo>",
      "subject": "[Searchlight -'${env}'] send DB backups cron failed",
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
DB_BACKUP_URL=https://$AZURE_BACKUP_STORAGE_ACCOUNT_NAME.blob.core.windows.net/$AZURE_DB_BACKUP_CONTAINER/

mkdir -p ./backups/temp-backups
# WARNING: DOUBLES DB BACKUP DISK SPACE TEMPORARILY!!
# AZCopy requires you to be the owner in order to send it, even if you have write permission
# Docker always saves backups as root
# This temporary copying is a workaround so that all of the temporary files will be owned by thi instead of root
cp ./backups/*.sql ./backups/temp-backups/
LOCAL_COPY_STATUS=$?
azcopy copy ./backups/temp-backups/ $DB_BACKUP_URL --recursive
AZ_COPY_STATUS=$?
rm -rf ./backups/temp-backups/
RM_STATUS=$?


if [ $LOCAL_COPY_STATUS -ne 0 ] || [ $AZ_COPY_STATUS -ne 0 ] || [ $RM_STATUS -ne 0 ]
  then
  echo "Could not send DB backups, sending error email"
  mailtext="Could not send DB backups on ${env}"
  bodyHTML="<p> $mailtext </p>"
  maildata='{
      "api_key": "'${api_key}'",
      "to": ["Brad Wells <brad@lovejustice.ngo>"],
      "sender": "Searchlight '${env}' Cron Alerts <system+'${env}'@lovejustice.ngo>",
      "subject": "[Searchlight - '${env}'] send DB backups cron failed",
      "html_body": "'${bodyHTML}'"
  }'
  curl --request POST \
   --url https://api.smtp2go.com/v3/email/send \
   --header 'Content-Type: application/json' \
   --data "$maildata"
  exit 1
fi