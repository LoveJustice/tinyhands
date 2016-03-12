from dreamsuite.private import SECRET_KEY
from django.contrib import messages
from unipath import Path
import os

import os
BASE_DIR = Path(__file__).ancestor(3)

SERVER_EMAIL = 'tnurkkala@cse.taylor.edu'

ADMIN_EMAIL_SENDER = SERVER_EMAIL
DEFAULT_FROM_EMAIL = SERVER_EMAIL

EMAIL_HOST = 'smtpcorp.com'
EMAIL_HOST_USER = 'tinyhands'
EMAIL_HOST_PASSWORD = 'TINY@2014'
EMAIL_PORT = 2525
EMAIL_USE_TLS = True

#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEBUG = False

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

FIXTURE_DIRS = (
    os.path.join(BASE_DIR, 'fixtures'),
    # os.path.join(BASE_DIR, 'dataentry/fixtures'),
)

AUTH_USER_MODEL = 'accounts.Account'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_URL = '/logout/'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'widget_tweaks',
    'bootstrapform',
    'imagekit',
    'storages',
    'dataentry',
    'accounts',
    'events',
    'portal',
    'budget',
    'util',
    'static_border_stations',
    'rest_api',
    'rest_framework',
    'django_extensions',
    'bootstrap_pagination',
)


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'dreamsuite.urls'

WSGI_APPLICATION = 'dreamsuite.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': os.environ['DB_HOST'],
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASS'],
        'PORT': os.environ['DB_PORT'],
    }
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kathmandu'

USE_I18N = False
USE_L10N = False
USE_TZ = True

DATETIME_FORMAT = "n.j.Y g:iA"
DATE_FORMAT = "n.j.Y"

STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
STATIC_ROOT = os.path.normpath(os.path.join(SITE_ROOT, "../static"))
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

MESSAGE_TAGS = {
    messages.constants.ERROR: 'danger'    # Fix up for Bootstrap.
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, "templates")
        ],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                "django.template.context_processors.request",
                'django.contrib.messages.context_processors.messages',
                "dataentry.context_processors.border_stations_processor",
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',            ]
        },
    },
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_api.pagination.DefaultPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}
