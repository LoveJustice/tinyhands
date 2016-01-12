FROM tutum/nginx
COPY nginx.conf /etc/nginx/nginx.conf
COPY thi-nginx.conf /etc/nginx/sites-enabled/default

RUN mkdir /nginx
WORKDIR /nginx
RUN touch access.log
RUN touch error.log
RUN chown -R www-data:www-data /nginx/

EXPOSE 80 443
CMD service nginx start
