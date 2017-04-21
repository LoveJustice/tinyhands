from .base import *

DEBUG = True
TEMPLATE_DEBUG = True

EMAIL_BACKEND = 'dreamsuite.test_email_backend.EmailBackend'

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'test',
    'USER': os.environ.get('PGUSER'),
    'PASSWORD': os.environ.get('PGPASSWORD'),
    'HOST': '127.0.0.1',
    'PORT': 5434,
  }
}