FROM amunn/searchlight-base:V20240220
MAINTAINER amunn33

COPY application/ /data/
WORKDIR /data/

CMD /bin/sh /data/bin/run.sh > /log/python.log 2>&1
