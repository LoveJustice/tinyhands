import json
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from export_import.google_sheet_import import GoogleSheetImport
from dataentry.models import Form, BorderStation

class Command(BaseCommand):
    def handle(self, *args, **options):
        link_form_string = open('etc/link_form_station.json', 'r').read()
        link_forms = json.loads(link_form_string)
        for form_data in link_forms:
            form_name = form_data['form']
            try:
                form = Form.objects.get(form_name=form_name)
                station_codes = form_data['station_codes']
                for station_code in station_codes:
                    try:
                        station = BorderStation.objects.get(station_code=station_code)
                        form.stations.add(station)
                    except ObjectDoesNotExist:
                        print('Could not find station code ' + station_code + 'for form' + form_name)
            except ObjectDoesNotExist:
                print('Could not find form with name ' + form_name)
            