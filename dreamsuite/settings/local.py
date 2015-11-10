from .base import *

DEBUG = True
TEMPLATE_DEBUG = True

SITE_DOMAIN = 'localhost:8080'

INSTALLED_APPS += ('corsheaders',)

MIDDLEWARE_CLASSES += (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
)

CORS_ORIGIN_ALLOW_ALL = True