#!/usr/bin/env bash

OLD_DBS="prod-old/db-2014-08-04-15-00.sqlite3
		prod-old/db-2015-07-19-17-01.sqlite3
		staging/db-2014-11-04-03-15.sqlite3"

NEW_DBS="tom/db-2015-06-15-17-11.sqlite3
		tom/db-2015-06-29-13:06.sqlite3
		tom/db-2015-07-18-11:00.sqlite3
		prod-new/db-2015-06-15-16-01.sqlite3
		prod-new/db-2015-07-19-17-01.sqlite3
		staging/db-2015-06-29-07-50.sqlite3
		staging/db-2015-06-30-07-50.sqlite3
		staging/db-2015-07-19-17-01.sqlite3"


ID=3

OLD_QUERY="select id, kind, interception_record_id, full_name, district, vdc
		  from dataentry_interceptee
		  where id = $ID;"

NEW_QUERY="select interceptee.id as 'Int ID', interceptee.kind as 'T/V',
		  interceptee.interception_record_id as 'IID',
		  interceptee.full_name as 'Name',
		  district.id as 'Dist ID', district.name as 'Dist Name',
		  vdc.id as 'VDC ID', vdc.name as 'VDC Name'
		  from dataentry_interceptee as interceptee
		  left outer join dataentry_district as district on interceptee.district_id = district.id
		  left outer join dataentry_vdc as vdc on interceptee.vdc_id = vdc.id
		  where interceptee.id = $ID;"

for db in $OLD_DBS
do
	result=$(echo $OLD_QUERY | sqlite3 $db)
	echo -e "OLD  $result\t\t$db"
done

for db in $NEW_DBS
do
	result=$(echo $NEW_QUERY | sqlite3 $db)
	echo -e "NEW  $result\t\t$db"
done
