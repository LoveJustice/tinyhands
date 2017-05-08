from .base import *

DEBUG = True

INSTALLED_APPS += [
    'corsheaders',
]

MIDDLEWARE_CLASSES += [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True
INSTALLED_APPS.append('debug_toolbar')

SPREADSHEET_CONFIG = {
    'IRF': {
        'key_column' : 'IRF Number',
        'export': {
            'spreadsheet': 'Tinyhands',
            'sheet':'IRF Entry',
            'export_function': 'export_import.irf_io.get_irf_export_rows',
            },
        'import': {
            'spreadsheet':'Tinyhands',
            'sheet':'IRF Import',
            'import_function': 'export_import.irf_io.import_irf_row',
            'status_column': 'Import Status',
            'issue_column': 'Import Issues',
            },
        },
    'VIF': {
        'key_column': 'VIF Number',
        'export': {
            'spreadsheet':'Tinyhands VIFs',
            'sheet':'VIF Entry',         
            'export_function': 'export_import.vif_io.get_vif_export_rows',
            },
        'import': {
            'spreadsheet':'Tinyhands VIFs',
            'sheet':'VIF Import',
            'import_function': 'export_import.vif_io.import_vif_row',
            'status_column': 'Import Status',
            'issue_column': 'Import Issues',
            },
        },
    'ADDRESS2': {
        'replace': {
            'spreadsheet':'Tinyhands',
            'sheet':'Address2 Export',
            }
        }
    }
