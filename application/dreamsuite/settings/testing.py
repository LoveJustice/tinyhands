from .base import *

DEBUG = True
TEMPLATE_DEBUG = True

SITE_DOMAIN = '0.0.0.0:8000'
CLIENT_DOMAIN = '0.0.0.0:8000/#'


EMAIL_BACKEND = 'dreamsuite.test_email_backend.EmailBackend'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'mydatabase',
    }
}
