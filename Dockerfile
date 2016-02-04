FROM python:2.7
MAINTAINER benaduggan

ENV PYTHONUNBUFFERED 1

# Make the directory for our code
RUN mkdir /data
WORKDIR /data

# Install linux dependencies
RUN apt-get update
RUN apt-get install -y python-dev libncurses5-dev libxml2-dev libxslt-dev zlib1g-dev libjpeg-dev

# Install pip dependencies
COPY application/ /data/
RUN chmod 777 /data/dreamsuite/static
RUN pip install -r requirements.txt

# Make the log files for Gunicorn
RUN mkdir -p /srv/logs
RUN touch /srv/logs/gunicorn.log
RUN touch /srv/logs/access.log
RUN chown -R www-data:www-data /srv/logs/
CMD /data/bin/run.sh
