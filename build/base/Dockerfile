#FROM python:3.6-alpine
FROM python:3-alpine3.6
MAINTAINER benaduggan
ENV PYTHONUNBUFFERED 1

ADD requirements.txt /requirements.txt
RUN apk update
RUN pip install --upgrade pip
RUN apk add make automake gcc g++ subversion openssl ca-certificates cmake linux-headers && update-ca-certificates && pip install numpy && pip install pandas

ENV OPENCV_VERSION=3.1.0
RUN mkdir /opt && cd /opt \
    && wget https://github.com/opencv/opencv/archive/${OPENCV_VERSION}.zip \
    && unzip ${OPENCV_VERSION}.zip \
    && rm -rf ${OPENCV_VERSION}.zip 

# Install and set up CMake and then Open CV - Warning, this takes absolutely forever

ENV CC /usr/bin/clang
ENV CXX /usr/bin/clang++



RUN mkdir -p /opt/opencv-${OPENCV_VERSION}/build \
    && cd /opt/opencv-${OPENCV_VERSION}/build \
    && cmake \
    -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D CMAKE_C_COMPILER=/usr/bin/gcc \
    -D CMAKE_CXX_COMPILER=/usr/bin/g++ \
    -D WITH_FFMPEG=NO \
    -D WITH_IPP=NO \
    -D WITH_OPENEXR=NO \
    -D WITH_TBB=YES \
    -D BUILD_EXAMPLES=NO \
    -D BUILD_ANDROID_EXAMPLES=NO \
    -D INSTALL_PYTHON_EXAMPLES=NO \
    -D BUILD_DOCS=NO \
    -D BUILD_opencv_python2=NO \
    -D BUILD_opencv_python3=ON \
    -D PYTHON3_EXECUTABLE=/usr/local/bin/python \
    -D PYTHON3_INCLUDE_DIR=/usr/local/include/python3.6m/ \
    -D PYTHON3_LIBRARY=/usr/local/lib/libpython3.so \
    -D PYTHON_LIBRARY=/usr/local/lib/libpython3.so \
    -D PYTHON3_PACKAGES_PATH=/usr/local/lib/python3.6/site-packages/ \
    -D PYTHON3_NUMPY_INCLUDE_DIRS=/usr/local/lib/python3.6/site-packages/numpy/core/include/ \
    .. && \
    make VERBOSE=1 && \
    make && \
    make install && \
    rm -rf /opt/opencv-${OPENCV_VERSION}


RUN echo -e '@edgunity http://nl.alpinelinux.org/alpine/edge/community\n\
@edge http://nl.alpinelinux.org/alpine/edge/main\n\
@testing http://nl.alpinelinux.org/alpine/edge/testing\n\
@community http://dl-cdn.alpinelinux.org/alpine/edge/community'\
  >> /etc/apk/repositories

# Install build deps, then run `pip install`, then remove unneeded build deps all in a single step.
RUN set -ex \
    && apk add --no-cache --virtual .build-deps \
            gcc \
            build-base \
            openblas-dev \
            unzip \
            wget \
            ncurses-dev \
            bash \
            readline \
            make \
            libc-dev \
            musl-dev \
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
            libjpeg \
            libjpeg-turbo-dev \
            libpng-dev \
            jasper-dev \
            tiff-dev \
            libwebp-dev \
            clang-dev \
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


WORKDIR /data