FROM python:2.7
MAINTAINER benaduggan

ENV PYTHONUNBUFFERED 1

# Install linux dependencies
RUN apt-get update && apt-get install -y python-dev libncurses5-dev libxml2-dev libxslt-dev zlib1g-dev libjpeg-dev s3cmd curl && pip install --upgrade pip

# Make the directory for our code
RUN mkdir /data
WORKDIR /data

# Install pip dependencies
ADD application/requirements.txt /data/requirements.txt
RUN pip install -r requirements.txt

# Make the log files for Gunicorn
RUN mkdir -p /log
RUN touch /log/gunicorn_access.log /log/gunicorn_error.log && chown -R www-data:www-data /log

# Copy application files over to container
COPY application/ /data/

# Run the application
CMD /data/bin/run.sh

RUN curl -o /usr/local/bin/s3-expand https://raw.githubusercontent.com/silinternational/s3-expand/master/s3-expand \
    && chmod a+x /usr/local/bin/s3-expand

ENTRYPOINT ["/usr/local/bin/s3-expand"]
CMD ["/data/bin/run.sh"]
