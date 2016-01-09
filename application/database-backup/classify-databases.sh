#!/usr/bin/env bash

# Figure out which database files contain the newer model for districts and VDCs.

for db in */db*
do
	if echo ".schema dataentry_interceptee" | sqlite3 $db | grep -q district_id
	then
	   echo NEW $db
	else
	   echo OLD $db
	fi
done | tr '/' ' ' | sort --key="3"
