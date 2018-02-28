import httplib2
import logging

from oauth2client.client import GoogleCredentials
from apiclient import discovery
from django.conf import settings

logger = logging.getLogger(__name__);

class GoogleSheetBasic:
    scope=( 
        "https://www.googleapis.com/auth/drive",
        "https://spreadsheets.google.com/feeds",
        "https://docs.google.com/feeds"
    )
    
    credentials = False
    http = None
    
    @staticmethod
    def get_credentials():
        try:
            
            credentials =  GoogleCredentials.get_application_default()
            credentials = credentials.create_scoped(GoogleSheetBasic.scope)
            GoogleSheetBasic.http = credentials.authorize(httplib2.Http())
            
            GoogleSheetBasic.credentials = True        
        except:
            logger.warn("No credentials file for google spreadsheet.  No update to google spreadsheets will be attempted.")
        
        if GoogleSheetBasic.credentials:    
            GoogleSheetBasic.drive_service = discovery.build('drive', 'v3', http=GoogleSheetBasic.http)
            discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
            GoogleSheetBasic.sheet_service = discovery.build('sheets', 'v4', http=GoogleSheetBasic.http,
                                                             discoveryServiceUrl = discoveryUrl)
        
    def find_spreadsheet(self, name):
        spreadsheet_id = None
        results = GoogleSheetBasic.drive_service.files().list().execute()
        items = results.get('files', [])
        if items:
            for item in items:
                if item['name'] == name:
                    spreadsheet_id = item['id']
                    break
                
        return spreadsheet_id
    
    def get_sheet_metadata(self):
        response = GoogleSheetBasic.sheet_service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
        sheets = response.get('sheets', [])
        found = False
        for sheet in sheets:
            if sheet['properties']['title'] == self.sheet_name:
                self.sheet_id = sheet['properties']['sheetId']
                self.rowCount = sheet['properties']['gridProperties']['rowCount']
                self.colCount = sheet['properties']['gridProperties']['columnCount']
                found = True
                break
            
        if not found:
            logger.error("Unable to locate sheet " + self.sheet_name)
    
    
    def __init__(self, spreadsheet_name, sheet_name):
        if GoogleSheetBasic.http is None:
            GoogleSheetBasic.get_credentials()
            
        logger.debug("after get credentials")
        
        self.spreadsheet_name = spreadsheet_name
        self.sheet_name = sheet_name;
        
        self.spreadsheet_id = self.find_spreadsheet(spreadsheet_name)
        if self.spreadsheet_id is None:
            logger.error("spreadsheet " + spreadsheet_name + " not found")
        self.get_sheet_metadata()
        
        logger.debug("after get metadata")
        
    @staticmethod
    def from_settings(data_type):
        sheet_settings = ['spreadsheet', 'sheet']
        
        data_setting = None
        if data_type in settings.SPREADSHEET_CONFIG:
            data_setting = settings.SPREADSHEET_CONFIG[data_type]
        else:
            logger.error('Unable to find setting for data type ' + data_type)
            return
        
        if 'replace' not in data_setting:
            logger.error('Unable to find export settings for data type ' + data_type)
            return
        
        for setting in sheet_settings:
            if setting not in data_setting['replace']:
                logger.error('Unable to find replace setting ' + setting + ' for data type ' + data_type)
                return
        
        return GoogleSheetBasic(
            data_setting['replace']['spreadsheet'],
            data_setting['replace']['sheet'])
        
    def delete_request(self, first_row, last_row):
        req = {
            "deleteDimension": {
                "range":{
                    "sheetId" : self.sheet_id,
                    "dimension" : "ROWS",
                    "startIndex" : first_row,
                    "endIndex" : last_row + 1
                }
            }
        }
        
        self.rowCount = self.rowCount - (last_row - first_row + 1)
        
        return req
        
    
    def expand_request(self, rows):
        req = {
        "appendDimension": {
                "sheetId" : self.sheet_id,
                "dimension" : "ROWS",
                "length" : rows
            }
        }
        
        self.rowCount = self.rowCount + rows
        
        return req
    
    def batch_update(self, reqs):
        body = {
            'requests' : reqs
        }
        
        response = GoogleSheetBasic.sheet_service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheet_id, body=body).execute()
        return response
    
    def convert_notation(self, row_index, column_index):
        notation = ''
        if column_index >= 26:
            notation += chr(column_index // 26 + 64)
        notation += chr(column_index % 26 + 65)
        if row_index is not None:
            notation += str(row_index)
        
        return notation
    
    def get_data(self, start_row, start_col, end_row, end_col, majorDimension = "ROWS"):
        rng = self.sheet_name + "!" + self.convert_notation(start_row, start_col) + ":" + self.convert_notation(end_row, end_col)
        
        result = GoogleSheetBasic.sheet_service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=rng, majorDimension=majorDimension).execute()
        if "values" in result:
            return result["values"]
        else:
            # No data in requested range
            return [[]]
    
    def update_cell(self, row, col, val):
        body = {
            "values":[[val]]
            }
        rng = self.sheet_name + "!" + self.convert_notation(row, col) + ":" + self.convert_notation(row, col)
        GoogleSheetBasic.sheet_service.spreadsheets().values().update(spreadsheetId=self.spreadsheet_id, range=rng, valueInputOption="USER_ENTERED", body=body).execute()

    def append_rows(self, vals):
        body = {
            "values": vals
            }
        rng = self.sheet_name + "!" + "A:ZZ"
        GoogleSheetBasic.sheet_service.spreadsheets().values().append(spreadsheetId=self.spreadsheet_id, range=rng, valueInputOption="USER_ENTERED", body=body).execute()
         
            
        
