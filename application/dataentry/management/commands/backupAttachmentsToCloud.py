import datetime
import hashlib
import logging
import os

from django.core.files import File
from django.core.files.storage import storages, Storage
from django.core.management import BaseCommand

logger = logging.getLogger(__name__)

# This takes local files from your default storage and uploads them to Azure.
# Started from:
# https://github.com/Krukov/django-storages-migrate/blob/master/storages/commands/management/commands/sync_media.py
# and later:
# https://github.com/jazzband/django-dbbackup/tree/af443c5026a480fffd33c4bbb6b4b1981e6700cb
# TODO - this does NOT work for AWS S3 -> Azure, only local -> Azure
class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("-d", "--date", type=str)
        parser.add_argument("-p", "--path", type=str)

    def handle(self, *args, **options):
        date_string = options["date"]
        date = None
        if date_string:
            date = datetime.datetime.strptime(date_string, "%Y-%m-%d")
        media_existing_storage_backend: Storage = storages['filesystem']
        media_backups_storage_backend: Storage = storages['mediabackups']

        for relative_path in self.explore_storage(media_existing_storage_backend):
            logger.debug('Checking backup of ' + relative_path)
            if options["path"]:
                if options["path"] not in relative_path:
                    logger.debug(f'Skipping {relative_path} because it does not contain {options["path"]}')
                    continue
            file_on_file_system: File = media_existing_storage_backend.open(relative_path)
            if date:
                mtime = os.path.getmtime(file_on_file_system.name)
                mtime_date = datetime.datetime.fromtimestamp(mtime)
                if mtime_date < date:
                    logger.debug(f'Skipping {relative_path} because ${mtime_date} is older than {date}')
                    continue
            is_on_azure = media_backups_storage_backend.exists(relative_path)
            bytes_on_file_system = file_on_file_system.read()
            if is_on_azure:
                file_on_azure: File = media_backups_storage_backend.open(relative_path)
                bytes_on_azure = file_on_azure.read()
                # Use this on text files for debugging
                # print(bytes_on_file_system, bytes_on_azure)
                hash_of_file_system = hashlib.md5(bytes_on_file_system).hexdigest()
                hash_of_azure = hashlib.md5(bytes_on_azure).hexdigest()
                if hash_of_azure != hash_of_file_system:
                    logger.debug(f'Hash of {relative_path} backup changed, replacing on Azure')
                    media_backups_storage_backend.delete(relative_path)
                    media_backups_storage_backend.save(relative_path, file_on_file_system)
                # else it is there and is the same, no action
            else:
                logger.debug(f'{relative_path} backup not in azure, adding to Azure')
                # Are you getting
                # ResourceNotFoundError: The specified container does not exist.
                # or ErrorCode:ContainerNotFound
                # here? Then you need to go to Azure in the Storage browser and make the (probably "media") blob container (aka folder).
                media_backups_storage_backend.save(relative_path, file_on_file_system)

    # Modified from source code of dbbackup's mediabackup.py
    def explore_storage(self, media_storage_backend) -> str:
        """Generator of all files contained in media storage."""
        relative_dirs = ['']
        while relative_dirs:
            relative_dir_path = relative_dirs.pop()
            # absolute_dir_path = os.path.join(root_path, relative_dir_path)
            subdirs, files = media_storage_backend.listdir(relative_dir_path)
            for media_filename in files:
                yield os.path.join(relative_dir_path, media_filename)
            relative_dirs.extend([os.path.join(relative_dir_path, subdir) for subdir in subdirs])