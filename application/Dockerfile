FROM python:2.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /data
WORKDIR /data
ADD ./requirements.txt /data/
RUN pip install -r requirements.txt
RUN chown -R www-data:www-data /data/

