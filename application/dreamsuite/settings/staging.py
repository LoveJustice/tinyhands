from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS += [
    'corsheaders',
]

MIDDLEWARE_CLASSES += [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True

ADMINS = [('Ben Duggan', 'benaduggan@gmail.com'), ('Austin Munn', "austin@tinyhands.org"), ("Stan Rishel", "scrishel@sbcglobal.net")]

IMPORT_ACCOUNT_EMAIL = 'ashishm@tinyhands.org'
SPREADSHEET_CONFIG = {
    'IRF': {
        'key_column' : 'IRF Number',
        'export': {
            'spreadsheet': 'Dream Suite - THN Data (Staging)',
            'sheet':'IRF Entry',
            'export_function': 'export_import.irf_io.get_irf_export_rows',
            },
        'import': {
            'spreadsheet':'Dream Suite - THN Data (Staging)',
            'sheet':'IRF Import',
            'import_function': 'export_import.irf_io.import_irf_row',
            'status_column': 'Import Status',
            'issue_column': 'Import Issues',
            },
        },
    'VIF': {
        'key_column': 'VIF Number',
        'export': {
            'spreadsheet':'Dream Suite - THN VIFs (Staging)',
            'sheet':'VIF Entry',
            'export_function': 'export_import.vif_io.get_vif_export_rows',
            },
        'import': {
            'spreadsheet':'Dream Suite - THN VIFs (Staging)',
            'sheet':'VIF Import',
            'import_function': 'export_import.vif_io.import_vif_row',
            'status_column': 'Import Status',
            'issue_column': 'Import Issues',
            },
        },
    'ADDRESS2': {
        'replace': {
            'spreadsheet':'Dream Suite - THN Data (Staging)',
            'sheet':'Address2 Export',
            }
        },
    'Traffickers': {
        'key_column': 'id',
        'export': {
            'spreadsheet':'Trafficker Photos',
            'sheet':'Interceptee_Photos',
            'export_function': 'export_import.trafficker_io.get_trafficker_export_rows',
            },
        }
    }