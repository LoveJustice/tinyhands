from .base import *

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '139.162.52.72',
    'staging.tinyhandsdreamsuite.org',
]

DEBUG = True

# ADMINS = [('Tom Nurkkala', 'tnurkkala@cse.taylor.edu')]
ADMINS = [('Ben Duggan', 'benaduggan@gmail.com'), ('Austin Munn', "austin@tinyhands.org")]
SITE_DOMAIN = 'staging.tinyhandsdreamsuite.org'
CLIENT_DOMAIN = 'staging.tinyhandsdreamsuite.org/beta/#'

SPREADSHEET_NAME = 'Dream Suite - THN Data (Staging)'
IRF_WORKSHEET_NAME = 'IRF Entry'
VIF_WORKSHEET_NAME = 'VIF Entry'

IMPORT_ACCOUNT_EMAIL = 'ashishm@tinyhands.org'
IMPORT_SPREADSHEET_NAME = 'Dream Suite - THN Data (Staging)'
IRF_IMPORT_WORKSHEET_NAME = 'IRF Import'