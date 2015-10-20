echo "######   Setting DJANGO_SETTINGS_MODULE to testing.   ######"
export DJANGO_SETTINGS_MODULE=dreamsuite.settings.testing

echo "######   Removing old test database.   ######"
rm ./e2etest.sqlite3

echo "######   Create new test database.   ######"
./manage.py syncdb --noinput

#import data to test database
echo "######   Load 'e2etesting/fixtures/*' into database.   ######"
./manage.py loaddata ./e2etesting/fixtures/border_stations.json
./manage.py loaddata ./e2etesting/fixtures/test_accounts.json
./manage.py loaddata ./e2etesting/fixtures/test_alerts.json
./manage.py loaddata ./e2etesting/fixtures/test_geo_code_locations.json
./manage.py loaddata ./e2etesting/fixtures/test_vif.json

echo "######   Start the server.   ######"
./manage.py runserver 0.0.0.0:8001