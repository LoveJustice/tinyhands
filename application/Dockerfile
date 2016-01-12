FROM python:2.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /data
WORKDIR /data
ADD ./requirements.txt /data/
RUN pip install -r requirements.txt

RUN mkdir -p /srv/logs
RUN touch /srv/logs/gunicorn.log
RUN touch /srv/logs/access.log
RUN chown -R www-data:www-data /srv/logs/
RUN usermod -u 1000 www-data
