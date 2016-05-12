#/bin/bash
TOP="$(pwd)"

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
    read -p "Do you want to continue and overwrite the file? " -n 1 -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]
    then
        exit 2
    fi
    echo
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
docker-compose run --rm web ./manage.py migrate
docker-compose run --rm web ./manage.py loaddata fixtures/sanitized-data.json
docker-compose run --rm web ./manage.py loaddata fixtures/sys-admin.json
