
if [ "$SITE_HOSTNAME" = "localhost" ]
then
  cat /etc/nginx/sites-enabled/local.conf.template > /etc/nginx/sites-enabled/default
else
  sed -e 's@${SITE_HOSTNAME}@'"$SITE_HOSTNAME"'@' -e 's@${SSL_CERT_PATH}@'"$SSL_CERT_PATH"'@' -e 's@${SSL_KEY_PATH}@'"$SSL_KEY_PATH"'@' /etc/nginx/sites-enabled/server.conf.template > /etc/nginx/sites-enabled/default
fi

service nginx start
