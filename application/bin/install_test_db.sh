#!/bin/bash

TOP="/data"

# source directories
DB_SRC="${TOP}/etc"
PHOTO_SRC="${TOP}/etc/interceptee_photos"
FORM_SRC="${TOP}/etc/scanned_forms"

if [ ! -f "${DB_SRC}/sanitized-data.json.gz" ]
then
    echo "You must be at the top directory for tinyhands"
    exit 1
fi

# destination directories
PHOTO="${TOP}/media/interceptee_photos"
IRF_FORM="${TOP}/media/scanned_irf_forms"
VIF_FORM="${TOP}/media/scanned_vif_forms"

if [ -e "${TOP}/fixtures/sanitized-data.json" ]
then
    echo "There is already a data file at ${TOP}/fixtures/sanitized-data.json, it will be overwritten!"
    echo "continuing..."
fi

cp "${DB_SRC}/sanitized-data.json.gz" "${TOP}/fixtures"
cd "${TOP}/fixtures"
gunzip -f sanitized-data.json.gz

mkdir -p "${PHOTO}"
mkdir -p "${IRF_FORM}"
mkdir -p "${VIF_FORM}"
mkdir -p "${TOP}/dreamsuite/static"

cd "${PHOTO_SRC}"
cp * "${PHOTO}"

cd "${FORM_SRC}"
cp * "${IRF_FORM}"
cp * "${VIF_FORM}"

# Fix permissions for Docker
chmod 777 "${PHOTO}" "${IRF_FORM}" "${VIF_FORM}" "${TOP}/media" "${TOP}/dreamsuite/static" "${TOP}/src"

# migrate and load db
cd "$TOP"
python /data/bin/wait_for_db.py

python /data/manage.py makemigrations
python /data/manage.py migrate
python /data/manage.py loaddata fixtures/sanitized-data.json
python /data/manage.py loaddata fixtures/initial-required-data/*
