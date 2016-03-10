docker-compose run --rm web python manage.py collectstatic --noinput
cp -a application/dreamsuite/static build/nginx/
cp -a application/media build/nginx/

docker build -t tusoftwarestudio/dreamsuite-nginx ./build/nginx/
docker build -t tusoftwarestudio/dreamsuite .
