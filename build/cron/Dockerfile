FROM ubuntu:latest
MAINTAINER benaduggan

# Copy in cron configuration
COPY build/cron/tinyhands-cron /etc/cron.d/
RUN chmod 0644 /etc/cron.d/tinyhands-cron
