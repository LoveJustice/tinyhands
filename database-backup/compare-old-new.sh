#!/usr/bin/env bash

OLD_DB=prod-old/db-2015-07-19-17-01.sqlite3

# This one was a correct migration -- everything matches
NEW_DB=tom/db-2015-06-15-17-11.sqlite3

# This is the next oldest one I have -- broken
#NEW_DB=tom/db-2015-06-29-13:06.sqlite3

# This is the newest one I have -- broken
#NEW_DB=prod-new/db-2015-07-19-17-01.sqlite3

OLD_QUERY="SELECT id, kind, interception_record_id, full_name, trim(district), trim(vdc)
		  FROM dataentry_interceptee;"

NEW_QUERY="SELECT interceptee.id, interceptee.kind,
interceptee.interception_record_id, interceptee.full_name,
trim(district.name), trim(vdc.name)
FROM dataentry_interceptee as interceptee
LEFT OUTER JOIN dataentry_district AS district ON interceptee.district_id = district.id
LEFT OUTER JOIN dataentry_vdc AS vdc ON interceptee.vdc_id = vdc.id;"

echo $OLD_QUERY | sqlite3 $OLD_DB > foo.old.txt
echo $NEW_QUERY | sqlite3 $NEW_DB > foo.new.txt

diff foo.{old,new}.txt
