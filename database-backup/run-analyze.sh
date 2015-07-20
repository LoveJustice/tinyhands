#!/usr/bin/env bash

./analyze.py											\
	--old-query-file=queries-old-model.sql				\
	--old-db-file=prod-old/db-2015-07-19-17-01.sqlite3	\
	--new-query-file=queries-new-model.sql				\
	--new-db-file=tom/db-2015-06-15-17-11.sqlite3		\
	--new-db-file=prod-new/db-2015-06-15-16-01.sqlite3	\
	--new-db-file=prod-new/db-2015-06-29-18-08.sqlite3	\
	--query-name=interceptee
