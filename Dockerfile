FROM python:2.7-alpine
MAINTAINER benaduggan

ENV PYTHONUNBUFFERED 1
ADD application/requirements.txt /requirements.txt

# Install build deps, then run `pip install`, then remove unneeded build deps all in a single step.

RUN set -ex \
    && apk add --no-cache --virtual .build-deps \
            gcc \
            build-base \
            ncurses-dev \
            bash \
            readline \
            readline-dev \
            patch \
            make \
            libc-dev \
            musl-dev \
            linux-headers \
            pcre-dev \
            postgresql-dev \
            python-dev \
            py-setuptools \
            libxml2-dev \
            libxslt-dev \
            zlib-dev \
            jpeg-dev \
            libjpeg \
            curl \
            rsync \
    && pip install -U pip \
    && LIBRARY_PATH=/lib:/usr/lib /bin/sh -c "pip install --no-cache -r /requirements.txt" \
    && runDeps="$( \
            scanelf --needed --nobanner --recursive /usr/local/lib/python2.7/ \
                    | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
                    | sort -u \
                    | xargs -r apk info --installed \
                    | sort -u \
    )" \
    && apk add --virtual .python-rundeps $runDeps \
    && apk del .build-deps

# Make the directory for our code
# RUN mkdir -p /data /log && chown -R www-data:www-data /log
RUN mkdir -p /data /log
WORKDIR /data

# Copy application files over to container
COPY application/ /data/

CMD ["/bin/sh", "/data/bin/run.sh > /log/python.log 2>&1"]
