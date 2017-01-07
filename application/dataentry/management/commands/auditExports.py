from django.core.management.base import BaseCommand

from export_import.google_sheet_audit import audit_exports


class Command(BaseCommand):
    def handle(self, *args, **options):
        audit_exports()