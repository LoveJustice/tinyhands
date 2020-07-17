import csv
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from dataentry.models import BorderStation, OperationsData

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='+', type=str)
        parser.add_argument('year', nargs='+', type=int)
        parser.add_argument('month', nargs='+', type=int)
    def handle(self, *args, **options):
        file_name = options.get('filename')[0]
        start_year = options.get('year')[0]
        start_month = options.get('month')[0]
        
        current_date = datetime.datetime.now()
        end_month = current_date.month
        end_year = current_date.year
        if (current_date.day < 6):
            end_month -= 2
        else:
            end_month -= 1
        if end_month < 1:
            end_month = 12 + end_month
            end_year -= 1
        
        name_map = {
            'Budget':'budget',
            'Int':'intercepts',
            'Ast':'arrests',
            'Gsp':'gospel',
            'Emp':'empowerment',
            'CIF':'cifs'
            }
        
        with open(file_name) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                station_code = row['Station Code']
                try:
                    station = BorderStation.objects.get(station_code=station_code)
                except ObjectDoesNotExist:
                    print ('Unable to find station with code', station_code)
                    continue
            
                month = start_month
                year = start_year
                
                while year*100+month <= end_year*100+end_month:
                    if month < 10:
                        str_month = '0' + str(month)
                    else:
                        str_month = str(month)
                    year_month = str(year) + str_month
                    year_month_csv = ' ' + str(year) + ' ' + str_month
                    
                    try:
                        entry = OperationsData.objects.get(station=station, year_month=year_month)
                    except ObjectDoesNotExist:
                        entry = OperationsData()
                        entry.station = station
                        entry.year_month = year_month
                    
                    for key in name_map.keys():
                        if key + year_month_csv in row:
                            value = row[key + year_month_csv]
                            value = value.replace(',','')
                            if value != '':
                                setattr(entry, name_map[key], value)
                    
                    entry.save()
                    
                    
                    month += 1
                    if month > 12:
                        year += 1
                        month = 1
                
                
                
            
            