from .base import *

DEBUG = True
TEMPLATE_DEBUG = True

SITE_DOMAIN = '0.0.0.0:8000'

INSTALLED_APPS += ('debug_toolbar',)

def prevent_tests_migrate(db):

    import django
    from django.db import connections
    from django.db.migrations.executor import MigrationExecutor
    django.setup()
    ma = MigrationExecutor(connections[db]).loader.migrated_apps
    return dict(zip(ma, ['{a}.notmigrations'.format(a=a) for a in ma]))

MIGRATION_MODULES = prevent_tests_migrate('default')