import csv
from django.core.management.base import BaseCommand
from dataentry.models import Country, Holiday

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('country', nargs='+', type=str)
        parser.add_argument('in-file', nargs='+', type=str)
    
    def handle(self, *args, **options):
        in_file = options['in-file'][0]
        country_name = options['country'][0]
        
        country = Country.objects.get(name=country_name)
        with open(in_file) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                duplicate = Holiday.objects.filter(country=country, holiday=row['Date (YYYY-MM-DD)'])
                if len(duplicate) == 0:
                    holiday = Holiday()
                    holiday.country = country
                    holiday.name = row['Public Holidays']
                    holiday.holiday = row['Date (YYYY-MM-DD)']
                    holiday.save()
                else:
                    print ('Duplicate of existing date for', country.name,'on ', row['Date (YYYY-MM-DD)'])