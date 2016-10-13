printf "\n\nPushing Dreamsuite Build Number: %s\n\n" "$1"

docker push tusoftwarestudio/dreamsuite-nginx:$1
docker push tusoftwarestudio/dreamsuite:$1
