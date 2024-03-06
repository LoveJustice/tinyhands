FROM python:3.9-slim
MAINTAINER bradleo99
ENV PYTHONUNBUFFERED 1

ADD requirements.txt /requirements.txt
RUN apt-get update
RUN pip install --upgrade pip
# Numpy and pandas are needed for matplotlib, not sure why they are in an earlier build step, though
RUN apt-get -y install \
#    I honestly don't know which of these I need, the build compiles without a single one \
#    Linux headers was not found in apt-get, the rest were \
     make \
     automake \
     gcc \
     g++ \
     subversion \
     openssl \
     ca-certificates \
     cmake \
#     linux-headers \
    && update-ca-certificates \
    && pip install numpy==1.26.0 \
    && pip install pandas==2.1.1

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install opencv-python==3.4.18.65

RUN apt install libcairo2-dev pkg-config python3-dev -y
RUN pip install pycairo

# IDEALLY - Install build deps, then run `pip install`, then remove unneeded build deps all in a single step.
# Not sure how to do that with apt-get
RUN set -ex \
#    --no-cache --virtual .build-deps \
#  Can't find equivalent of grouping virtual build deps in apt-get \
#  Therefore makes it hard to remove unneeded ones later \
    && apt-get -y install \
        gcc \
        libxml2-dev \
        libxslt-dev \
        ncurses-dev \
        libpq-dev \
        libffi-dev \
    && pip install -U pip \
    && LIBRARY_PATH=/lib:/usr/lib /bin/sh -c "pip install --no-cache-dir -r /requirements.txt"
#    && runDeps="$( \
#            scanelf --needed --nobanner --recursive /usr/local/lib/python3.6/ \
#                    | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
#                    | sort -u \
#                    | xargs -r apk info --installed \
#                    | sort -u \
#    )" \
#    && apk add --virtual .python-rundeps $runDeps \
#    && apk del .build-deps

# Make the directory for our code and logging
RUN mkdir -p /data /log


WORKDIR /data