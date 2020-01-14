from django.core.management.base import BaseCommand

from export_import.google_sheet_audit import audit_exports


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--form',
            action='append',
            type=str,
            help='Specify the name of a form to audit',
        )
        
    def handle(self, *args, **options):
        audit_exports(options['form'])