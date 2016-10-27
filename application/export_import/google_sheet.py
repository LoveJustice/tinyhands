from google_sheet_basic import GoogleSheetBasic
from google_sheet_names import spreadsheet_header_from_export_header

import logging

logger = logging.getLogger(__name__);

class GoogleSheet (GoogleSheetBasic):
    extra_allocation  = 20
    def __init__(self, spreadsheet_name, sheet_name, key_column_name, export_method):
        GoogleSheetBasic.__init__(self, spreadsheet_name, sheet_name)
        logger.debug("In __init__")
        self.column_map = None
        self.get_column_names()
        self.export_method = export_method
        
        self.find_key_column(key_column_name)
        logger.debug("After find key column")
        self.refresh_keys()
        logger.debug("After refresh keys")
        
        
    def get_column_names(self):
        results = self.get_data(1, 0, 1, self.colCount-1)
        self.column_names = results[0]
        
    def find_key_column(self, name):
        self.key_column_index = None
        for idx in range(len(self.column_names)):
            if self.column_names[idx] == name:
                self.key_column_name = name
                self.key_column_index = idx
                break
        
        if self.key_column_index is None:
            logger.error("Unable to find key column with name=" + name)
                
    def refresh_keys(self):
        results = self.get_data(2,self.key_column_index, None, self.key_column_index, majorDimension="COLUMNS")
        self.key_values = results[0]
        
    def map_headers(self, headers):
        column_map = []
        for column_idx in range(len(self.column_names)):
            column_map.append(None)
            for export_idx in range(len(headers)):
                if spreadsheet_header_from_export_header(self.column_names[column_idx]) == spreadsheet_header_from_export_header(headers[export_idx]):
                    column_map[column_idx] = export_idx
                    break
            if column_map[column_idx] == None:
                logger.warn( "Export does not contain data for column " + self.column_names[column_idx])
        
        self.column_map = column_map
        
    def map_export_to_columns(self, rows):
        if self.column_map == None:
            self.map_headers(rows[0])
            
        mapped_rows = []
        for data_idx in range(1,len(rows)):
            mapped_row = []
            for col_idx in range(len(self.column_map)):
                if self.column_map[col_idx] is not None and self.column_map[col_idx] < len(rows[data_idx]):
                    mapped_row.append(str(rows[data_idx][self.column_map[col_idx]]))
                else:
                    mapped_row.append(None)
            
            mapped_rows.append(mapped_row)
        
        return mapped_rows
    
    def append_premapped_rows(self, mapped_rows):
        self.refresh_keys()
        empty_rows = self.rowCount - len(self.key_values) - 1
        if empty_rows < len(mapped_rows):
            expand_rows = len(mapped_rows) - empty_rows + GoogleSheet.extra_allocation
            reqs = [self.expand_request(expand_rows)]
            self.batch_update(reqs)
            
        GoogleSheetBasic.append_rows(self, mapped_rows)
        
    def append_rows(self, rows):
        mapped_rows = self.map_export_to_columns(rows)
        self.append_premapped_rows(mapped_rows)
        
    def update(self, key_value, new_object):
        if new_object is None:
            new_mapped = []
        else:
            new_rows = self.export_method([new_object])
            logger.debug("row count returned by export method = " + str(len(new_rows)))
            new_mapped = self.map_export_to_columns(new_rows)
        
        self.refresh_keys()
        
        reqs = []
        for key_idx in range(len(self.key_values)):
            if self.key_values[key_idx] == key_value:
                logger.debug("delete row index=" + str(key_idx + 1))
                reqs.insert(0,self.delete_request(key_idx+1, key_idx+1))
        
        remaining = self.rowCount - len(self.key_values) - 1
        if remaining < len(new_mapped):
            expand = len(new_mapped) - remaining + GoogleSheet.extra_allocation
            logger.debug("expanding table rows by " + str(expand))
            reqs.append(self.expand_request(expand))
        
        if len(reqs) > 0:
            self.batch_update(reqs)
        
        if len(new_mapped) > 0:
            logger.debug("Adding rows to table " + str(len(new_mapped)))
            self.append_premapped_rows(new_mapped)
        
    def audit(self, db_data, key_field):
        sheet_keys = {}
        for key in self.key_values:
            sheet_keys[key] = True
        
        db_data_to_export = []
        for db_obj in db_data:
            key_value = getattr(db_obj, key_field)
            if not key_value in sheet_keys:
                db_data_to_export.append(db_obj)
                logger.debug("audit - export " + key_value + "for sheet " + self.sheet_name)
                
        new_rows = self.export_method(db_data_to_export)
        logger.debug("export_method returned row count " + str(len(new_rows)))
        self.append_rows(new_rows)                    