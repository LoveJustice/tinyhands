from .base import *

DEBUG = False

ADMINS = (('Tom Nurkkala', 'tnurkkala@cse.taylor.edu'),('Austin Munn', 'austin_munn@taylor.edu'))

SITE_DOMAIN = 'tinyhandsdreamsuite.org'

ALLOWED_HOSTS = [
    'tinyhandsdreamsuite.org',
    'localhost',
    '127.0.0.1',
    '172.31.34.90',
    '54.68.250.225',
    '68.45.130.175'
]

SPREADSHEET_NAME = 'Dream Suite - THN Data'
IRF_WORKSHEET_NAME = 'IRF Entry'
VIF_WORKSHEET_NAME = 'VIF Entry'