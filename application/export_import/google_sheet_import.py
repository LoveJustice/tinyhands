from google_sheet import GoogleSheet
from google_sheet_names import spreadsheet_header_from_export_header
from irf_io import import_irf_row, get_irf_export_rows
from vif_io import import_vif_row, get_vif_export_rows

from django.conf import settings

import logging

logger = logging.getLogger(__name__);

class GoogleSheetImport (GoogleSheet):
    READY_TO_IMPORT = 'Ready'
    DUPLICATE_IMPORT = 'Existing'
    REJECTED_IMPORT = 'Rejected'
    IMPORT_SUCESS = 'Imported'
    
    def __init__(self, spreadsheet_name, sheet_name, key_column_name, export_method, issue_column, id_column_name, import_method):
        GoogleSheet.__init__(self, spreadsheet_name, sheet_name, export_method)
        self.issue_column = issue_column
        self.id_column_name = id_column_name
        
        for col_idx in range(self.colCount):
            if spreadsheet_header_from_export_header(self.key_values[col_idx]) == spreadsheet_header_from_export_header(issue_column):
                self.issue_idx = col_idx
        
    def import_rows(self):
        for key_idx in range(len(self.key_values)):
            if self.key_values[key_idx] == GoogleSheetImport.READY_TO_IMPORT:
                row_idx = key_idx + 2
                row_data = self.get_data(row_idx, 1, row_idx, self.colCount)
                
                data = {}
                for col_idx in range(self.colCount):
                    data[spreadsheet_header_from_export_header(self.column_names[col_idx])] = row_data[col_idx]
                    
                errList = self.import_method(data)
                if len(errList) > 0:
                    if errList[0] == 'Form already exists':
                        self.update(row_idx, self.key_column_index, GoogleSheetImport.DUPLICATE_IMPORT)
                        self.update(row_idx, self.issue_column, errList[0])
                    else:
                        logger.debug("Rejected " + data[spreadsheet_header_from_export_header(self.key_column_name)])
                        self.update(row_idx, self.key_column_index, GoogleSheetImport.REJECTED_IMPORT)
                        sep = ""
                        err_string = ""
                        for err in errList:
                            err_string = err_string + sep + err
                            sep = '\n'
                            
                        self.update(row_idx, self.issue_column, err_string)
                else:
                    self.update(row_idx, self.key_column_index, GoogleSheetImport.IMPORT_SUCCESS)
                    self.update(key_idx+2, self.issue_column, "")
                    
    @staticmethod
    def import_irfs():
        import_sheet = GoogleSheetImport(settings.SPREADSHEET_NAME, settings.IRF_IMPORT_WORKSHEET_NAME, 'Import Status', get_irf_export_rows, 'Import Issues', 'IRF number', import_irf_row)
        import_sheet.import_rows()
        
    @staticmethod
    def import_vifs():
        import_sheet = GoogleSheetImport(settings.SPREADSHEET_NAME, settings.VIF_IMPORT_WORKSHEET_NAME, 'Import Status', get_vif_export_rows, 'Import Issues', 'VIF number', import_vif_row)
        import_sheet.import_rows()
        
        
        