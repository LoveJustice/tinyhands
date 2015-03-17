#start webdriver server
webdriver-manager start &

#Change settings to test
export DJANGO_SETTINGS_MODULE=dreamsuite.settings.testing

#delete old test database
rm test.sqlite3

#recreate test database
./manage.py syncdb --noinput

#import data to test database
./manage.py loaddata e2etesting/fixtures/*

#start your django server
./manage.py runserver 0.0.0.0:8001 &

#make sure the webdriver and django server have time to spin up
sleep 10

#run the tests
protractor e2etesting/conf.js

