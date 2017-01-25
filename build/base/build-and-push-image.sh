#!/bin/bash

docker build --no-cache -t tusoftwarestudio/tinyhands-base .
docker push tusoftwarestudio/tinyhands-base
