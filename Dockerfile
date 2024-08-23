FROM amunn/searchlight-base:V20240220
MAINTAINER amunn33

COPY application/ /data/
WORKDIR /data/

# Temporary until searchlight-base with new requirements.txt in build/base/Dockerfile is created
RUN pip install django-storages[azure]
RUN pip install azure-identity

CMD /bin/sh /data/bin/run.sh > /log/python.log 2>&1
