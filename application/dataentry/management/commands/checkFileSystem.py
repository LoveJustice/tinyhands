import os
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('file_system', nargs='+', type=str)
        parser.add_argument('percent', nargs='+', type=int)
        
    def handle(self, *args, **options):
        file_system = options.get('file_system')[0]
        percent = options.get('percent')[0]
        
        statvfs = os.statvfs(file_system)
        free_percent = statvfs.f_bfree * 100 / statvfs.f_blocks
        if free_percent < percent:
            admins = settings.ADMINS
            to_list = []
            for admin in admins:
                to_list.append(admin[1])
            send_mail('Low file system space',
                      'File system "' + file_system + '" has ' + str(free_percent) + '% free',
                      None,
                      to_list)

