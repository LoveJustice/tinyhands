echo "######   Starting webdriver server.   ######"
webdriver-manager start >/dev/null 2>&1 &

echo "######   Setting DJANGO_SETTINGS_MODULE to testing.   ######"
export DJANGO_SETTINGS_MODULE=dreamsuite.settings.testing

echo "######   Removing old test database.   ######"
rm test.sqlite3

echo "######   Create new test database.   ######"
./manage.py syncdb --noinput

#import data to test database
echo "######   Load 'e2etesting/fixtures/*' into database.   ######"
./manage.py loaddata e2etesting/fixtures/border_stations.json
./manage.py loaddata e2etesting/fixtures/test_accounts.json
./manage.py loaddata e2etesting/fixtures/test_alerts.json
./manage.py loaddata e2etesting/fixtures/test_geo_code_locations.json
./manage.py loaddata e2etesting/fixtures/test_vif.json

echo "######   Start the server.   ######"
./manage.py runserver 0.0.0.0:8001 &

echo "######   Wait a while so the webdriver and django server are ready.   ######"
sleep 10

echo "######   Run the tests as specified in 'e2etesting/conf.js'.   ######"
protractor e2etesting/conf.js

echo "######   Kill all remaining processes.   ######"
kill 0
