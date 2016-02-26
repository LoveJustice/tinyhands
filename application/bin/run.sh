#!/bin/bash
./manage.py migrate                  # Apply database migrations
./manage.py collectstatic --noinput  # Collect static files

# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn --config=bin/gunicorn_config.py dreamsuite.wsgi:application
