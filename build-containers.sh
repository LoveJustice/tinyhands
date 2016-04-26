docker-compose run --rm web python manage.py collectstatic --noinput &>/dev/null # redirected cause it's annoying
cp -a application/dreamsuite/static build/nginx/
cp -a application/media build/nginx/

TAG=$(date +%s)

docker build -t tusoftwarestudio/dreamsuite-nginx:$TAG ./build/nginx/
docker build -t tusoftwarestudio/dreamsuite:$TAG .

docker-compose run --rm web python manage.py collectstatic -l --noinput &>/dev/null  # redirected cause it's annoying

echo $TAG > dreamsuite_tag

printf "\n\nDreamsuite Build Number: %s\n\n" "$TAG"
