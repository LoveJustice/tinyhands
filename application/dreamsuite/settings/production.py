from .base import *

STATICFILES_LOCATION = 'static'
MEDIAFILES_LOCATION = 'media'


DEBUG = True

ADMINS = (('Tom Nurkkala', 'tnurkkala@cse.taylor.edu'),('Austin Munn', 'austin_munn@taylor.edu'))

SITE_DOMAIN = 'tinyhandsdreamsuite.org'

AWS_QUERYSTRING_AUTH = False
AWS_STORAGE_BUCKET_NAME = 'dreamsuite-media'
AWS_ACCESS_KEY_ID = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_ACCESS_KEY_ID']
# AWS_S3_CUSTOM_DOMAIN = 'https://s3-ap-southeast-1.amazonaws.com/%s' % AWS_STORAGE_BUCKET_NAME


AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME


STATIC_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN
MEDIA_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, MEDIAFILES_LOCATION)
from dataentry.custom_storages import *
DEFAULT_FILE_STORAGE = 'dataentry.custom_storages.MediaStorage'
STATICFILES_STORAGE = 'dataentry.custom_storages.StaticStorage'

SPREADSHEET_NAME = 'Dream Suite - THN Data'
IRF_WORKSHEET_NAME = 'IRF Entry'
VIF_WORKSHEET_NAME = 'VIF Entry'
