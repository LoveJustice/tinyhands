from .base import *



DEBUG = True

ADMINS = (('Ben Duggan', 'benjamin_duggan@taylor.edu'))

SITE_DOMAIN = 'tinyhandsdreamsuite.org'


# We use S3 in production to serve media files so these are configuration variables for accessing that
AWS_QUERYSTRING_AUTH = False
AWS_STORAGE_BUCKET_NAME = os.environ['BUCKET_NAME']
AWS_ACCESS_KEY_ID = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_ACCESS_KEY_ID']
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME


STATICFILES_LOCATION = 'static'
MEDIAFILES_LOCATION = 'media'

# STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, STATICFILES_LOCATION)
MEDIA_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, MEDIAFILES_LOCATION)
from dataentry.custom_storages import *
DEFAULT_FILE_STORAGE = 'dataentry.custom_storages.MediaStorage'
# STATICFILES_STORAGE = 'dataentry.custom_storages.StaticStorage'

SPREADSHEET_NAME = 'Dream Suite - THN Data'
IRF_WORKSHEET_NAME = 'IRF Entry'
VIF_WORKSHEET_NAME = 'VIF Entry'
