FROM tutum/nginx

# Add our nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf
COPY thi-nginx.conf /etc/nginx/sites-enabled/default

# Make a directory for the nginx logs
RUN mkdir /nginx
WORKDIR /nginx
RUN touch access.log
RUN touch error.log
RUN chown -R www-data:www-data /nginx/

# For access to the sites on SSL and not
EXPOSE 80 443
CMD service nginx start
