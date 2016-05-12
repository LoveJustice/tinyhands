from .base import *

DEBUG = True

INSTALLED_APPS += [
    'corsheaders',
]

MIDDLEWARE_CLASSES += [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True
INSTALLED_APPS.append('debug_toolbar')

SITE_DOMAIN = 'localhost'

SPREADSHEET_NAME = 'Tinyhands'
IRF_WORKSHEET_NAME = 'IRF Entry'
VIF_WORKSHEET_NAME = 'VIF Entry'
