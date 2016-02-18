from .base import *

DEBUG = True
TEMPLATE_DEBUG = True

INSTALLED_APPS += (
    'corsheaders',
    'rest_framework.authtoken',
)

MIDDLEWARE_CLASSES += (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
)

CORS_ORIGIN_ALLOW_ALL = True

SITE_DOMAIN = 'localhost' 