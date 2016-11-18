from .base import *

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '139.162.52.72',
    'staging.tinyhandsdreamsuite.org',
]

DEBUG = True

ADMINS = [('Ben Duggan', 'benaduggan@gmail.com'), ('Austin Munn', "austin@tinyhands.org"), ("Stan Rishel", "scrishel@sbcglobal.net")]

SITE_DOMAIN = 'https://staging.tinyhandsdreamsuite.org'
CLIENT_DOMAIN = 'https://staging.tinyhandsdreamsuite.org/#'

SPREADSHEET_NAME = 'Dream Suite - THN Data (Staging)'
IRF_WORKSHEET_NAME = 'IRF Entry'
VIF_WORKSHEET_NAME = 'VIF Entry'
ADDRESS2_WORKSHEET_NAME = 'Address2 Export'

IMPORT_ACCOUNT_EMAIL = 'ashishm@tinyhands.org'
IMPORT_SPREADSHEET_NAME = 'Dream Suite - THN Data (Staging)'
IRF_IMPORT_WORKSHEET_NAME = 'IRF Import'
VIF_IMPORT_WORKSHEET_NAME = 'VIF Import'
