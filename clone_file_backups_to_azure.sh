set -a
source ./staging.env
set +a

set -e

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