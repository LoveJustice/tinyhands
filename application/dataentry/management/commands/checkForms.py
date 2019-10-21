from django.core.management.base import BaseCommand

from dataentry.models import Form


class Command(BaseCommand):
    def handle(self, *args, **options):
        forms = Form.objects.filter(form_type__name__in=['IRF','CIF','VDF'])
        for form in forms:
            form_class = form.storage.get_form_storage_class()
            stations = list(form.stations.all())
            non_matching = form_class.objects.all().exclude(station__in=stations)
            non_match_list = []
            for non_match in non_matching:
                non_match_list.append(non_match.get_key())
            
            if len(non_match_list) > 0:
                print(form.form_name, 'station not associated with form', non_match_list)
            
            non_conform_list = []
            for non_conform in form_class.objects.all():
                if not non_conform.get_key().startswith(non_conform.station.station_code):
                    non_conform_list.append(non_conform.get_key())
            
            if len(non_conform_list) > 0:
                print (form.form_name, 'form number does not start with station code', non_conform_list)
                
            
