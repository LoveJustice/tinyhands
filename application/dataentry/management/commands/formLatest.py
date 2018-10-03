import subprocess
import unicodedata

from django.conf import settings
from django.core.management.base import BaseCommand
from django.apps import apps

from dataentry.models.form_migration import FormMigration


class Command(BaseCommand):
    def handle(self, *args, **options):
        form_data_file = settings.BASE_DIR + '/fixtures/initial-required-data/form_data.json'
        cmd = 'sum ' + form_data_file
        rslt = subprocess.check_output(cmd, shell=True)
        parts = " ".join("".join(map(chr, rslt)).strip().split()).split()
        print ('Checksum values', parts)
        FormMigration.check_load_form_data(apps, form_data_file, parts)