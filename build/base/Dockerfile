FROM python:2.7
MAINTAINER benaduggan

ENV PYTHONUNBUFFERED 1
WORKDIR /data

# Install linux dependencies
RUN apt-get update && apt-get install -y python-dev libncurses5-dev libxml2-dev libxslt-dev zlib1g-dev libjpeg-dev s3cmd curl rsync && pip install --upgrade pip

RUN mkdir -p /data/

# Install pip dependencies
ADD requirements.txt /data/requirements.txt
RUN pip install -r requirements.txt
