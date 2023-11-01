#!/bin/bash

docker build --no-cache -t amunn/searchlight-base .
docker push amunn/searchlight-base
