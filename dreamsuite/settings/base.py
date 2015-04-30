from dreamsuite.private import SECRET_KEY
from django.contrib import messages
from unipath import Path

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

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEBUG = False
TEMPLATE_DEBUG = False

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
FIXTURE_DIRS = (
    (os.path.join(SITE_ROOT, '../../fixtures/'),)
)

STATICFILES_DIRS = (os.path.join(SITE_ROOT, '../../static/'),
                    os.path.join(SITE_ROOT, '../../budget/templates/budget/javascript/'),
                    os.path.join(SITE_ROOT, '../../portal/templates/portal/javascript/'),
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
    'dataentry',
    'accounts',
    'portal',
    'budget',
    'util',
    'rest_framework',
    'static_border_stations',
    'bootstrap_pagination',
)

import django.conf.global_settings as DEFAULT_SETTINGS
TEMPLATE_CONTEXT_PROCESSORS = DEFAULT_SETTINGS.TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.request',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'dreamsuite.urls'

WSGI_APPLICATION = 'dreamsuite.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kathmandu'

USE_I18N = False
USE_L10N = False
USE_TZ = True

DATETIME_FORMAT = "n.j.Y g:iA"
DATE_FORMAT = "n.j.Y"

STATIC_URL = '/static/'

MESSAGE_TAGS = {
    messages.constants.ERROR: 'danger'    # Fix up for Bootstrap.
}

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, "templates"),
)

TEMPLATE_CONTEXT_PROCESSORS += ("dataentry.context_processors.border_stations_processor", )

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    )
}
