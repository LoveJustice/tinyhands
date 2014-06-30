from private import SECRET_KEY

import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SERVER_EMAIL = 'DreamSuiteAdmin@tinyhands.org'
EMAIL_HOST = 'smtpcorp.com'

EMAIL_PORT = 2525
EMAIL_HOST_USER = 'tinyhands'
EMAIL_HOST_PASSWORD = 'TINY@2014'
EMAIL_USE_TLS = True

ADMIN_EMAIL_SENDER = SERVER_EMAIL
DEFAULT_FROM_EMAIL = SERVER_EMAIL
SITE_DOMAIN = 'tinyhandsdreamsuite.org'
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

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
    'widget_tweaks',
    'bootstrapform',
    'imagekit',
    'dataentry',
    'accounts',
    'util',
    'south',
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

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, "templates"),
)

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
