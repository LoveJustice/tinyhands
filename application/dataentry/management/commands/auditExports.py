from django.core.management.base import BaseCommand

from dataentry.csv_io import *
from dataentry.google_sheets import GoogleSheetClientThread

class Command(BaseCommand):
    def handle(self, *args, **options):
        GoogleSheetClientThread.audit_export_forms()