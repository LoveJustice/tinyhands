#!/bin/bash
echo migrate database...
/usr/local/bin/python /data/manage.py migrate --noinput        # Apply database migrations

# Start Gunicorn processes
echo Starting Gunicorn.
/usr/local/bin/gunicorn --config=/data/bin/gunicorn_config.py dreamsuite.wsgi:application
