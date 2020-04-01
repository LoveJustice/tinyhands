import datetime
from django.core.management.base import BaseCommand
from django.conf import settings

from export_import.google_sheet import GoogleSheet
from export_import.data_indicator_io import get_data_collection_indicator_export_rows, get_data_entry_indicator_export_rows

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('indicatorType', nargs='+', type=str)
        parser.add_argument(
            '--year_month',
            action='append',
            type=str,
            help='Specify the year and month for processing. "202003" for March 2020',
        )
    
    def export_entry_indicators (self, year_month):
        spreadsheet = 'Data Indicators' + settings.SPREADSHEET_SUFFIX
        sheet = GoogleSheet(spreadsheet,'Entry', 'year month', get_data_entry_indicator_export_rows)
        sheet.update(year_month, year_month)
    
    def export_collection_indicators(self, year_month):
        spreadsheet = 'Data Indicators' + settings.SPREADSHEET_SUFFIX
        sheet = GoogleSheet(spreadsheet,'Collection', 'year month', get_data_collection_indicator_export_rows)
        sheet.update(year_month, year_month)
        
    def handle(self, *args, **options):
        indicator_type = options.get('indicatorType')[0].lower()
        if options.get('year_month'):
            year_month = options.get('year_month')[0]
        else:
            now = datetime.datetime.now()
            if now.month  == 1:
                year_month = str(now.year - 1)
            else:
                year_month = str(now.year)
            if now.month < 11:
                if now.month == 1:
                    year_month += '12'
                else:
                    year_month += '0' + str(now.month - 1)
            else:
                year_month += str(now.month)
        if indicator_type == 'collection':    
            self.export_collection_indicators(year_month)
        elif indicator_type =='entry':
            self.export_entry_indicators(year_month)
        else:
            print ('Unknown indicator type:', indicator_type)