docker build -t tusoftware-studio/dreamsuite-nginx ./build/nginx/
docker build -t tusoftware-studio/dreamsuite-js-cli -f Dockerfile-js-cli .
docker build -t tusoftware-studio/dreamsuite .

docker-compose build
docker-compose up -d
