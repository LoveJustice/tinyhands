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

# Colgan's hacks to make tests run faster.
# Use a faster (and unsecure) hash.
'''PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',)

# Don't run migrations, just use the current models.
def prevent_tests_migrate(db):

    import django
    from django.db import connections
    from django.db.migrations.executor import MigrationExecutor
    django.setup()
    ma = MigrationExecutor(connections[db]).loader.migrated_apps
    return dict(zip(ma, ['{a}.notmigrations'.format(a=a) for a in ma]))'''

MIGRATION_MODULES = prevent_tests_migrate('default')
