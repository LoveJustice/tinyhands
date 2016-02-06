docker build -t tusoftwarestudio/dreamsuite-nginx ./build/nginx/
docker build -t tusoftwarestudio/dreamsuite-js-cli -f Dockerfile-js-cli .
docker build -t tusoftwarestudio/dreamsuite .

docker push tusoftwarestudio/dreamsuite-nginx
docker push tusoftwarestudio/dreamsuite-js-cli
docker push tusoftwarestudio/dreamsuite