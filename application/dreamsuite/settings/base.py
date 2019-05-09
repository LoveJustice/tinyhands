from django.contrib import messages
from unipath import Path
import os
import sys
import logging.config
import datetime

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

SITE_DOMAIN = os.environ['SITE_DOMAIN']
CLIENT_DOMAIN = os.environ['CLIENT_DOMAIN']
FCM_KEY_PATH = os.environ['FCM_KEY_PATH']

BASE_DIR = Path(__file__).ancestor(3)

SERVER_EMAIL = 'support@dreamsuite.org'

BORDER_STATION_EMAIL_SENDER = "sheital@tinyhands.org"
ADMIN_EMAIL_SENDER = SERVER_EMAIL
DEFAULT_FROM_EMAIL = SERVER_EMAIL

EMAIL_HOST = 'smtpcorp.com'
EMAIL_PORT = 2525
EMAIL_USE_TLS = True

ALERT_INTERVAL_IN_DAYS = 30

DEBUG = False

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

FIXTURE_DIRS = (
    os.path.join(BASE_DIR, 'fixtures'),
)

AUTH_USER_MODEL = 'accounts.Account'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_URL = '/logout/'
EXPIRING_TOKEN_LIFESPAN = datetime.timedelta(hours=10)

INSTALLED_APPS = [
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
    'dataentry',
    'firebase',
    'accounts',
    'events',
    'portal',
    'budget',
    'util',
    'static_border_stations',
    'rest_api',
    'rest_framework',
    'django_extensions',
    'rest_framework.authtoken',
    'django_filters'
]


MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

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

TEST_ENVIRONMENT = len(sys.argv) > 1 and sys.argv[1] == 'test'

MESSAGE_TAGS = {
    messages.constants.ERROR: 'danger'  # Fix up for Bootstrap.
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
                'django.template.loaders.app_directories.Loader',
            ]
        },
    },
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'accounts.expiring_token_authentication.ExpiringTokenAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_api.pagination.DefaultPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format':
              '%(levelname)s|%(asctime)s|%(name)s[%(lineno)s-%(funcName)s]>> %(message)s',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename':os.environ['DREAMSUITE_LOG'],
            'formatter':'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'export_import': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'export_import.google_sheet_work_queue': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'dataentry': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'budget.views': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

logging.config.dictConfig(LOGGING)
