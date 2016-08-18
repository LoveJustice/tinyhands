from .base import *

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '139.162.35.242',
    'tinyhandsdreamsuite.org',
]

ADMINS = (('Ben Duggan', 'benaduggan@gmail.com'), ("Austin Munn", 'austin@tinyhands.org'))
SITE_DOMAIN = 'https://tinyhandsdreamsuite.org'
CLIENT_DOMAIN = 'https://tinyhandsdreamsuite.org/beta/#'

SPREADSHEET_NAME = 'Dream Suite - THN Data'
IRF_WORKSHEET_NAME = 'IRF Entry'
VIF_WORKSHEET_NAME = 'VIF Entry'

IMPORT_ACCOUNT_EMAIL = 'ashishm@tinyhands.org'
IMPORT_SPREADSHEET_NAME = 'Dream Suite - THN Data'
IRF_IMPORT_WORKSHEET_NAME = 'IRF Import'
VIF_IMPORT_WORKSHEET_NAME = 'VIF Import'
