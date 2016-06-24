from django.core.management.base import BaseCommand
import csv

from dataentry.csv_io import *
from dataentry.google_sheets import GoogleSheetClientThread

class Command(BaseCommand):
	def handle(self, *args, **options):
		GoogleSheetClientThread.import_irfs()