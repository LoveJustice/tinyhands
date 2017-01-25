#!/bin/bash

# If these are not set, automatically set them to those defaults for testing purposes
${SSL_CERT_PATH:="/test/ssl_cert.pem"}
${SSL_KEY_PATH:="/test/ssl_key.pem"}

echo SSL_CERT_PATH: $SSL_CERT_PATH
echo SSL_KEY_PATH: $SSL_KEY_PATH

# If local development, use one nginx config, else use another one
if [ "$SITE_HOSTNAME" = "localhost" ]
then
  cat /etc/nginx/sites-enabled/local.conf.template > /etc/nginx/sites-enabled/default
else
  sed -e 's@${SITE_HOSTNAME}@'"$SITE_HOSTNAME"'@' -e 's@${SSL_CERT_PATH}@'"$SSL_CERT_PATH"'@' -e 's@${SSL_KEY_PATH}@'"$SSL_KEY_PATH"'@' /etc/nginx/sites-enabled/server.conf.template > /etc/nginx/sites-enabled/default
fi

echo This is the nginx sites-enabled file being used
cat /etc/nginx/sites-enabled/default
service nginx start