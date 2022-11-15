FROM tusoftwarestudio/tinyhands-base:latest
MAINTAINER benaduggan

COPY application/ /data/
WORKDIR /data/


# This needs to go into build/base/Dockerfile, its for cryptography
RUN apk add gcc musl-dev python3-dev libffi-dev openssl-dev cargo clang clang-dev

# Put any new libraries you are testing here, before adding them to build/base/requirements.txt
RUN pip install requests~=2.22.0
RUN pip install cryptography~=38.0.3
RUN pip install django-cors-headers~=3.1.1
RUN pip install drf-jwt~=1.19.2
RUN pip install pyjwt~=1.7.1

CMD /bin/sh /data/bin/run.sh > /log/python.log 2>&1
