from django.core.management.base import BaseCommand

from export_import.google_sheet_import import GoogleSheetImport


class Command(BaseCommand):
    def handle(self, *args, **options):
        GoogleSheetImport.import_data('VIF')