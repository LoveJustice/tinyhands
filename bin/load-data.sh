#!/bin/sh

# Load initial data fixtures when creating a new database

./manage.py loaddata fixtures/accounts.json
./manage.py loaddata fixtures/portal/border_stations.json
./manage.py loaddata fixtures/alerts/alerts.json
