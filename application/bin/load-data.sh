#!/bin/sh
# Load initial data fixtures when creating a new database

# echo "Loading accounts..."
# ./manage.py loaddata fixtures/accounts.json
# echo "Loading border stations..."
# ./manage.py loaddata fixtures/portal/border_stations.json
# echo "Loading alerts..."
# ./manage.py loaddata fixtures/alerts/alerts.json
# echo "Loading locations..."
# ./manage.py loaddata dataentry/fixtures/district.json
# ./manage.py loaddata dataentry/fixtures/vdc.json
# echo "Loading vifs..."
# ./manage.py loaddata fixtures/vifs.json
# echo "Loading irfs..."
# ./manage.py loaddata fixtures/irfs.json

echo "Loading sanitized data..."
./manage.py loaddata fixtures/sanitized-data.json
