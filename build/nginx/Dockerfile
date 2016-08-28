FROM nginx
MAINTAINER benaduggan

# Make a directory for the nginx logs
RUN mkdir -p /data/dreamsuite/static/ /data/media/ /log /test

# Copy in static files
COPY media/ /data/media/
COPY static/ /data/dreamsuite/static/
COPY test /test
COPY robots.txt /

# Add our nginx configuration
COPY run.sh /run.sh
COPY nginx.conf /etc/nginx/nginx.conf
COPY local.conf.template /etc/nginx/sites-enabled/local.conf.template
COPY server.conf.template /etc/nginx/sites-enabled/server.conf.template
RUN chown -R www-data:www-data /log /etc/nginx/sites-enabled/ /test

EXPOSE 80 443
CMD ["/bin/sh", "-c", "/run.sh > /log/nginx.log 2>&1"]