from .base import *

DEBUG = True
TEMPLATE_DEBUG = True

SITE_DOMAIN = '0.0.0.0:8000'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'test.sqlite3'),
    }
}