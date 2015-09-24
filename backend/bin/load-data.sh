#!/bin/sh

# Load initial data fixtures when creating a new database

echo "Loading accounts..."
./manage.py loaddata fixtures/accounts.json
echo "Loading border stations..."
./manage.py loaddata fixtures/portal/border_stations.json
echo "Loading alerts..."
./manage.py loaddata fixtures/alerts/alerts.json
echo "Loading locations..."
./manage.py loaddata fixtures/geo-code-locations.json
echo "Loading vifs..."
./manage.py loaddata fixtures/vifs.json
echo "Loading irfs..."
./manage.py loaddata fixtures/irfs.json
