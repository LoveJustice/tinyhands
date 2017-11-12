FROM tusoftwarestudio/tinyhands-base:latest
MAINTAINER benaduggan

COPY application/ /data/
CMD ["/bin/sh", "/data/bin/run.sh > /log/python.log 2>&1"]
