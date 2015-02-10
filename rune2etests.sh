#start your django server
./manage.py runserver 0.0.0.0:6000 &

#start webdriver server
nodejs node_modules/protractor/bin/webdriver-manager start &

#make sure the webdriver and django server have time to spin up
sleep 10

#run the tests
nodejs node_modules/protractor/bin/protractor e2etesting/conf.js

#shutdown all of the processes I spun up
kill 0
