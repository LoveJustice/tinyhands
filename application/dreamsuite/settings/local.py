from .base import *

DEBUG = True

INSTALLED_APPS.append('debug_toolbar')

SITE_DOMAIN = 'localhost'

SPREADSHEET_NAME = 'Tinyhands'
IRF_WORKSHEET_NAME = 'IRF Entry'
VIF_WORKSHEET_NAME = 'VIF Entry'

IMPORT_ACCOUNT_EMAIL = 'test_sup@example.com'
IMPORT_SPREADSHEET_NAME = 'Tinyhands'
IRF_IMPORT_WORKSHEET_NAME = 'IRF Import'
