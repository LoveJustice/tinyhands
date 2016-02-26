FROM nginx
MAINTAINER benaduggan

# Add our nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf
COPY thi-nginx.conf /etc/nginx/sites-enabled/default

# Make a directory for the nginx logs
RUN mkdir -p /data/dreamsuite/static/ /data/media/

# Copy in static files
COPY media/ /data/media/
COPY static/ /data/dreamsuite/static/

RUN mkdir -p /log
WORKDIR /log
RUN touch /log/nginx_access.log /log/nginx_error.log
RUN chown -R www-data:www-data /log/

EXPOSE 80
CMD service nginx start
