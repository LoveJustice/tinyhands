FROM amunn/searchlight:latest
MAINTAINER amunn33

# Copy in cron configuration
COPY tinyhands-cron /etc/cron.d/
RUN chmod 0644 /etc/cron.d/tinyhands-cron

# RUN mkdir -p /root/.aws/
# COPY conf/ /root/.aws/

RUN apt-get update && apt-get install -y \
  s3cmd curl

RUN curl -o /usr/local/bin/s3-expand https://raw.githubusercontent.com/silinternational/s3-expand/master/s3-expand \
    && chmod a+x /usr/local/bin/s3-expand

ENTRYPOINT ["/usr/local/bin/s3-expand"]
