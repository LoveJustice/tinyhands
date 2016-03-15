#!/bin/sh
# Load initial data fixtures when creating a new database

echo "Loading sanitized data..."
./manage.py loaddata fixtures/sanitized-data.json
