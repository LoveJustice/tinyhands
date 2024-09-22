import subprocess
from pathlib import Path

import unicodedata

from django.conf import settings
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import transaction, DEFAULT_DB_ALIAS

from dataentry.models.form_migration import FormMigration


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Hacky replacement to work on my local windows bash
        path_string = settings.BASE_DIR.replace('C:', '/mnt/c')
        form_data_file = Path(path_string).as_posix() + '/fixtures/initial-required-data/form_data*.json'
        # 'bash -c' needed for windows with Git Bash, 'sum' won't be found under CMD
        # It should still work the same on linux, it is just looks wierd that a shell is opening a shell again
        # TODO we should replace this checksum with a pure python one if possible to run on windows
        cmd = 'bash -c \'sum ' + form_data_file + '\''
        rslt = subprocess.check_output(cmd, shell=True)
        #print('result', rslt)
        parts = " ".join("".join(map(chr, rslt)).strip().split()).split()
        checksum = {}
        if len(parts) == 2:
            checksum['form_data.json'] = {
                    'checksum': int(parts[0]),
                    'blocks': int(parts[1])
                }
        else:
            for idx in range(0, len(parts), 3):
                checksum[parts[idx+2].split('/')[-1]] = {
                        'checksum': int(parts[idx]),
                        'blocks': int(parts[idx+1])
                }
        print ('checksum values')
        print (checksum)
        with transaction.atomic(using=DEFAULT_DB_ALIAS):
            FormMigration.check_load_form_data(apps, checksum)