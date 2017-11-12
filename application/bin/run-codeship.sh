#!/bin/bash

cd /data/

#wait for db to be available before running tests
/usr/local/bin/python /data/bin/wait_for_db.py

/usr/local/bin/python manage.py test
