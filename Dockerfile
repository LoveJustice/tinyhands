FROM python:2.7
MAINTAINER benaduggan

ENV PYTHONUNBUFFERED 1

# Install linux dependencies
RUN apt-get update && apt-get install -y python-dev libncurses5-dev libxml2-dev libxslt-dev zlib1g-dev libjpeg-dev s3cmd curl rsync && pip install --upgrade pip

# Make the directory for our code
RUN mkdir /data /log && chown -R www-data:www-data /log
WORKDIR /data

# Install pip dependencies
ADD application/requirements.txt /data/requirements.txt
RUN pip install -r requirements.txt

# Copy application files over to container
COPY application/ /data/

CMD ["/bin/sh", "-c", "/data/bin/run.sh > /log/python.log 2>&1"]
