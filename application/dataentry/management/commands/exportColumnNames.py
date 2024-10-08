from django.core.management.base import BaseCommand

from dataentry.models import GoogleSheetConfig
from export_import.export_form import ExportFormFactory, ExportToGoogleSheetFactory

class Command(BaseCommand):
    def handle(self, *args, **options):
        form_factory = ExportFormFactory()
        factory = ExportToGoogleSheetFactory()
        sheets = GoogleSheetConfig.objects.all()
        for sheet in sheets:
            stations = sheet.export_import.form.stations.all()
            if len(stations) < 1:
                continue
            station = stations[0]
            form_type = sheet.export_import.form.form_type
            export_forms = form_factory.find(station, form_type)
            google_sheet = factory.find(export_forms[0])
            
            string_val = '"' + sheet.spreadsheet_name + '","' + sheet.sheet_name +'"'
            for col in google_sheet.rows[0]:
                string_val = string_val + ',"' + col + '"'
            
            print (string_val)
            
            