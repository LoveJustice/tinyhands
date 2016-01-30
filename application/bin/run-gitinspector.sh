#!/bin/sh -x

# --grading enables
#   --hard
#   --list-file-types
#   --metrics
#   --responsibilities
#   --timeline
#   --weeks

# To get HTML:
#   --format=html

gitinspector \
	--file-types=coffee,py,sh,js,html,conf \
	--grading \
	--since='02/01/2015' \
	--exclude='media/' \
	--exclude='migrations/' \
	--exclude='static/KML' \
	--exclude='static/bootstrap' \
	--exclude='static/datatable' \
	--exclude='static/datetimepicker' \
	--exclude='static/fonts' \
	--exclude='static/images' \
	--exclude='static/jquery' \
	--exclude='static/less' \
	--exclude='static/.*?less' \
#	--format=html > foo.html
