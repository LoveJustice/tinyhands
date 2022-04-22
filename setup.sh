#!/bin/bash

echo "Checking for local.env file..."

if [ -e "local.env" ]
then
   echo "There is already a local.env file, it will be overwritten!"
   read -p "Do you want to overwrite the file? " -n 1 -r
   if [[ $REPLY =~ ^[Yy]$ ]]
   then
       echo ""
       echo "Creating local.env file..."
       cp local.env.dist local.env
   else
       echo ""
       echo "Skip creating local.env file..."    
   fi
else
    echo "Creating local.env file..."
    cp local.env.dist local.env    
fi


echo "Building containers..."
docker-compose build

docker-compose kill
docker-compose rm -f db
docker-compose run --rm web python ./bin/wait_for_db.py

mkdir -p backups
cp application/etc/sanitized_backup.sql backups/sanitized_backup.sql
# OD also has a postgres container. Adding version was a hacky way for it to get Searchlight's
CONTAINER_ID=`docker ps | grep postgres:9.6 | awk '{print $1}'`
echo "Container $CONTAINER_ID"
COMMAND="cat /backups/sanitized_backup.sql | psql -U postgres -d postgres"

echo "Initializing and installing sanitized data..."
docker exec $CONTAINER_ID sh -c ''"$COMMAND"''

docker-compose run --rm web sh ./bin/install_test_db.sh

echo "Load form data"
docker-compose run --rm web python ./manage.py formLatest

#echo "Linking forms with stations..."
#docker-compose run --rm web python ./manage.py linkFormStation

echo "Collecting Static files and symlinking them..."
docker-compose run --rm web python ./manage.py collectstatic -l --noinput
