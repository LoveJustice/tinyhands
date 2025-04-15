#!/bin/bash

docker-compose run --rm web python manage.py collectstatic --noinput
cp -a application/dreamsuite/static build/nginx/
cp -a application/media build/nginx/

TAG=`git log --format="%H" -n 1`

docker build --no-cache -t amunn/searchlight-nginx:$TAG ./build/nginx/
docker build --no-cache -t amunn/searchlight:$TAG .

docker-compose run --rm web python manage.py collectstatic -l --noinput

echo $TAG > dreamsuite_tag

printf "\n\nSearchlight Build Number: %s\n\n" "$TAG"
