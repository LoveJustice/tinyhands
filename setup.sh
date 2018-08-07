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


echo "Initializing and installing sanitized data..."
docker-compose run --rm web sh ./bin/install_test_db.sh

echo "Linking forms with stations..."
docker-compose run --rm web python ./manage.py linkFormStation

echo "Collecting Static files and symlinking them..."
docker-compose run --rm web python ./manage.py collectstatic -l --noinput
