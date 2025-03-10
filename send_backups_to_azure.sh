# MUST BE RUN WITH THI USER

set -a
source ./staging.env
set +a

set -e

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
azcopy copy ./backups/temp-backups/ $DB_BACKUP_URL --recursive
rm -rf ./backups/temp-backups/