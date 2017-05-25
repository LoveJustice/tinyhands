from google_sheet import GoogleSheet
from google_sheet_names import spreadsheet_header_from_export_header

from django.conf import settings

import importlib
import logging

logger = logging.getLogger(__name__);

class GoogleSheetImport (GoogleSheet):
    READY_TO_IMPORT = 'Ready'
    DUPLICATE_IMPORT = 'Existing'
    REJECTED_IMPORT = 'Rejected'
    IMPORT_SUCCESS = 'Imported'
    
    def __init__(self, spreadsheet_name, sheet_name, key_column_name, export_method, issue_column, id_column_name, import_method):
        GoogleSheet.__init__(self, spreadsheet_name, sheet_name, key_column_name, None)
        self.issue_column = issue_column
        self.id_column_name = id_column_name
        self.import_method = import_method
        
        for col_idx in range(len(self.column_names)):
            if spreadsheet_header_from_export_header(self.column_names[col_idx]) == spreadsheet_header_from_export_header(issue_column):
                self.issue_idx = col_idx
        
    def import_rows(self):
        for key_idx in range(len(self.key_values)):
            if self.key_values[key_idx] == GoogleSheetImport.READY_TO_IMPORT:
                row_idx = key_idx + 2
                row_data = self.get_data(row_idx, 0, row_idx, self.colCount)[0]
                
                data = {}
                for col_idx in range(len(self.column_names)):
                    if col_idx >= len(row_data) or row_data[col_idx] == '':
                        data[spreadsheet_header_from_export_header(self.column_names[col_idx])] = None
                    else:
                        data[spreadsheet_header_from_export_header(self.column_names[col_idx])] = row_data[col_idx]
                    
                errList = self.import_method(data)
                if len(errList) > 0:
                    if errList[0] == 'Form already exists':
                        self.update_cell(row_idx, self.key_column_index, GoogleSheetImport.DUPLICATE_IMPORT)
                        self.update_cell(row_idx, self.issue_idx, errList[0])
                    else:
                        self.update_cell(row_idx, self.key_column_index, GoogleSheetImport.REJECTED_IMPORT)
                        sep = ""
                        err_string = ""
                        for err in errList:
                            err_string = err_string + sep + err
                            sep = '\n'
                            
                        self.update_cell(row_idx, self.issue_idx, err_string)
                else:
                    self.update_cell(row_idx, self.key_column_index, GoogleSheetImport.IMPORT_SUCCESS)
                    self.update_cell(key_idx+2, self.issue_idx, " ")
    
    @staticmethod
    def import_data(data_type):
        import_settings = ['spreadsheet', 'sheet', 'import_function', 'status_column', 'issue_column']
        
        data_setting = None
        if data_type in settings.SPREADSHEET_CONFIG:
            data_setting = settings.SPREADSHEET_CONFIG[data_type]
        else:
            logger.error('Unable to find setting for data type ' + data_type)
            return
        
        if 'key_column' not in data_setting:
            logger.error('Unable to find key_column for data type' + data_type)
        
        if 'import' not in data_setting:
            logger.error('Unable to find import settings for data type ' + data_type)
            return
        
        for setting in import_settings:
            if setting not in data_setting['import']:
                logger.error('Unable to find import setting ' + setting + ' for data type ' + data_type)
                return
            
        mod_name, func_name = data_setting['import']['import_function'].rsplit('.',1)
        mod = importlib.import_module(mod_name)
        func = getattr(mod, func_name)
        
        import_sheet = GoogleSheetImport(
                data_setting['import']['spreadsheet'],
                data_setting['import']['sheet'],
                data_setting['import']['status_column'],
                None,
                data_setting['import']['issue_column'],
                data_setting['key_column'],
                func)
        import_sheet.import_rows()

        
        