#/bin/bash

if [ -z ${VIRTUAL_ENV} ]
then
    echo "You must be in a virtual environment"
    exit 1
fi

TOP="${VIRTUAL_ENV}/tinyhands"

# source directories
DB_SRC="${TOP}/etc/base_db"
PHOTO_SRC="${TOP}/etc/interceptee_photos"
FORM_SRC="${TOP}/etc/scanned_forms"


# destination directories
PHOTO="${TOP}/media/interceptee_photos"
IRF_FORM="${TOP}/media/scanned_irf_forms"
VIF_FORM="${TOP}/media/scanned_irf_forms"

if [ -e ${TOP}/db.sqlite3 ]
then
    echo "There is already a database file at ${TOP}/db.sqlite3"
fi

cp ${DB_SRC}/db.sqlite3 ${TOP}

mkdir -p ${PHOTO}
mkdir -p ${IRF_FORM}
mkdir -p ${VIF_FORM}

cd ${PHOTO}
cp ${PHOTO_SRC}/* .

cd ${IRF_FORM}
cp ${FORM_SRC}/* .

cd ${VIF_FORM}
cp ${FORM_SRC}/* .


