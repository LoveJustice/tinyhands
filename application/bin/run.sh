#!/bin/bash
python /data/manage.py migrate --noinput                  # Apply database migrations

# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn --config=bin/gunicorn_config.py dreamsuite.wsgi:application
