from django.core.management.base import BaseCommand

from export_import.google_sheets import GoogleSheetClientThread

class Command(BaseCommand):
    def handle(self, *args, **options):
        GoogleSheetClientThread.import_vifs()