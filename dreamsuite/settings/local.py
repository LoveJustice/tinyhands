from .base import *

DEBUG = True
TEMPLATE_DEBUG = True

SITE_DOMAIN = 'localhost:8080'

INSTALLED_APPS += ('debug_toolbar',)

class DisableMigrations(object):

    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return "notmigrations"

MIGRATION_MODULES = DisableMigrations()
