printf "\n\nPushing Searchlight Build Number: %s\n\n" "$1"

docker push amunn/searchlight-nginx:$1
docker push amunn/searchlight:$1
