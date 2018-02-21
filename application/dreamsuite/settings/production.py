from .base import *

ALLOWED_HOSTS = [
    '139.162.35.242',
    'tinyhandsdreamsuite.org',
    'dreamsuite.org',
]

ADMINS = [('Ben Duggan', 'benaduggan@gmail.com'), ('Austin Munn', "austin@tinyhands.org"), ("Stan Rishel", "scrishel@sbcglobal.net")]

IMPORT_ACCOUNT_EMAIL = 'ashishm@tinyhands.org'
SPREADSHEET_CONFIG = {
    'IRF': {
        'key_column' : 'IRF Number',
        'export': {
            'spreadsheet': 'Dream Suite - THN Data',
            'sheet':'IRF Entry',
            'export_function': 'export_import.irf_io.get_irf_export_rows',
            },
        'import': {
            'spreadsheet':'Dream Suite - THN Data',
            'sheet':'IRF Import',
            'import_function': 'export_import.irf_io.import_irf_row',
            'status_column': 'Import Status',
            'issue_column': 'Import Issues',
            },
        },
    'VIF': {
        'key_column': 'VIF Number',
        'export': {
            'spreadsheet':'Dream Suite - THN VIFs',
            'sheet':'VIF Entry',
            'export_function': 'export_import.vif_io.get_vif_export_rows',
            },
        'import': {
            'spreadsheet':'Dream Suite - THN VIFs',
            'sheet':'VIF Import',
            'import_function': 'export_import.vif_io.import_vif_row',
            'status_column': 'Import Status',
            'issue_column': 'Import Issues',
            },
        },
    'ADDRESS2': {
        'replace': {
            'spreadsheet':'Dream Suite - THN Data',
            'sheet':'Address2 Export',
            }
        }
    }
