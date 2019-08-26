FROM python:3.6-alpine
MAINTAINER benaduggan
ENV PYTHONUNBUFFERED 1

ADD requirements.txt /requirements.txt

# Install build deps, then run `pip install`, then remove unneeded build deps all in a single step.
RUN set -ex \
    && apk add --no-cache --virtual .build-deps \
            gcc \
            build-base \
            ncurses-dev \
            bash \
            readline \
            make \
            libc-dev \
            musl-dev \
            linux-headers \
            pcre-dev \
            postgresql-dev \
            python-dev \
            libxml2-dev \
            libxslt-dev \
            zlib-dev \
            jpeg-dev \
            libjpeg \
            curl \
            rsync \ 
            python-opencv \ 
            libopencv-dev \ 
            libav-tools  \ 
            libjpeg-dev \ 
            libpng-dev \ 
            libtiff-dev \ 
            libjasper-dev \ 
            libgtk2.0-dev \ 
            python-numpy \ 
            python-pycurl \ 
            libatlas-base-dev \
            webp \ 
            python-opencv \ 
            qt5-default \
            libvtk6-dev \ 
            zlib1g-dev \
    && pip install -U pip \
    && LIBRARY_PATH=/lib:/usr/lib /bin/sh -c "pip install --no-cache-dir -r /requirements.txt" \
    && runDeps="$( \
            scanelf --needed --nobanner --recursive /usr/local/lib/python3.6/ \
                    | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
                    | sort -u \
                    | xargs -r apk info --installed \
                    | sort -u \
    )" \
    && apk add --virtual .python-rundeps $runDeps \
    && apk del .build-deps

# Make the directory for our code and logging
RUN mkdir -p /data /log

# Install Open CV - Warning, this takes absolutely forever
RUN mkdir -p ~/opencv cd ~/opencv && \
    wget https://github.com/opencv/opencv/archive/4.1.0.zip && \
    unzip 4.1.0.zip && \
    rm 4.1.0.zip && \
    mv opencv-4.1.0 OpenCV && \
    cd OpenCV && \
    mkdir build && \ 
    cd build && \
    cmake \
    -DWITH_QT=ON \ 
    -DWITH_OPENGL=ON \ 
    -DFORCE_VTK=ON \
    -DWITH_TBB=ON \
    -DWITH_GDAL=ON \
    -DWITH_XINE=ON \
    -DBUILD_EXAMPLES=ON .. && \
    make -j4 && \
    make install && \ 
    ldconfig

WORKDIR /data