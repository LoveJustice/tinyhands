docker build -t tusoftware-studio/dreamsuite-nginx -f Dockerfile-nginx .
docker build -t tusoftware-studio/dreamsuite .
docker build -t tusoftware-studio/dreamsuite-js-cli -f Dockerfile-js-cli .

docker-compose build
docker-compose up -d
