from django.core.management.base import BaseCommand
import csv

from dataentry.csv_io import *
from dataentry.google_sheets import GoogleSheetClientThread

class Command(BaseCommand):
	def add_arguments(self, parser):
		parser.add_argument('in_file', nargs='+', type=str)
		parser.add_argument('out_file', nargs='+', type=str)
		
	def handle(self, *args, **options):
		in_file = options['in_file'][0]
		with open(in_file) as csvfile:
			reader = csv.DictReader(csvfile)
			results = join_irf_export_rows(reader)
		
		file_name = str(options['out_file'][0])
		with open(file_name, 'w') as csvfile:
			writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
			writer.writerows(results)