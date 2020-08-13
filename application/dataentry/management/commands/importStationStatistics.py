import csv
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from dataentry.models import BorderStation, StationStatistics, LocationStatistics, LocationStaff
from static_border_stations.models import Location, Staff

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('mode', nargs='+', type=str)
        parser.add_argument('filename', nargs='+', type=str)
        parser.add_argument('startYearMonth', nargs='+', type=int)
        parser.add_argument('endYearMonth', nargs='+', type=int)
    def handle(self, *args, **options):
        mode = options.get('mode')[0]
        file_name = options.get('filename')[0]
        start_year_month = options.get('startYearMonth')[0]
        end_year_month = options.get('endYearMonth')[0]
        
        start_year = int(start_year_month/100)
        start_month = start_year_month % 100
        end_year = int(end_year_month/100)
        end_month = end_year_month % 100
        
        self.station_map = {
            'Budget':'budget',
            'Gsp':'gospel',
            'Emp':'empowerment',
            'CIF':'cifs',
            }
        self.location_map = {
            'Int':'intercepts',
            'Ast':'arrests',
            }
        self.staff_map = {
            'Staff':'work_fraction'
            }
        
        if (mode == 'station_pre'):
            self.processStationStatistics(file_name, start_year, start_month, end_year, end_month, True)
        elif (mode == 'station_post'):
            self.processStationStatistics(file_name, start_year, start_month, end_year, end_month, False)
        elif (mode == 'location'):
            self.processLocationStatistics(file_name, start_year, start_month, end_year, end_month);
        
    
    def processLocationStatistics(self, file_name, start_year, start_month, end_year, end_month):
        skip = False
        with open(file_name) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                tmp_station_code = row['Station Code']
                tmp_location = row['Location']
                if tmp_location == 'TOTAL' or tmp_location == '':
                    continue
                if tmp_location != '' and tmp_location != 'TOTAL' and len(tmp_station_code) == 3:
                    station_code = tmp_station_code
                    try:
                        station = BorderStation.objects.get(station_code=station_code)
                        skip = False
                    except ObjectDoesNotExist:
                        print ('Unable to find station with code', station_code)
                        skip = True
                        continue
                elif skip:
                    continue
                
                try:
                    location = Location.objects.get(border_station=station, name__iexact=tmp_location)
                except ObjectDoesNotExist:
                    print('Unable to find location with name', tmp_location)
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
                        entry = LocationStatistics.objects.get(location=location, year_month=year_month)
                    except ObjectDoesNotExist:
                        entry = LocationStatistics()
                        entry.location = location
                        entry.year_month = year_month
                    
                    modified = False
                    for key in self.location_map.keys():
                        if key + year_month_csv in row:
                            value = row[key + year_month_csv]
                            value = value.replace(',','')
                            if value != '':
                                setattr(entry, self.location_map[key], value)
                                modified = True
                    if modified:
                            entry.save()
                    
                    general_staff = Staff.get_or_create_general_staff(station)
                    try:
                        entry = LocationStaff.objects.get(location=location, staff=general_staff, year_month=year_month)
                    except ObjectDoesNotExist:
                        entry = LocationStaff()
                        entry.location = location
                        entry.staff = general_staff
                        entry.year_month = year_month
                    
                    modified = False
                    for key in self.staff_map.keys():
                        if key + year_month_csv in row:
                            value = row[key + year_month_csv]
                            value = value.replace(',','')
                            if value != '':
                                setattr(entry, self.staff_map[key], value)
                                modified = True
                    if modified:
                            entry.save()
                    
                    month += 1
                    if month > 12:
                        year += 1
                        month = 1
                        
                        
    def processStationStatistics(self, file_name, start_year, start_month, end_year, end_month, include_arrests_and_staff):
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
                        entry = StationStatistics.objects.get(station=station, year_month=year_month)
                    except ObjectDoesNotExist:
                        entry = StationStatistics()
                        entry.station = station
                        entry.year_month = year_month
                    
                    for key in self.station_map.keys():
                        if key + year_month_csv in row:
                            value = row[key + year_month_csv]
                            value = value.replace(',','')
                            if value != '':
                                setattr(entry, self.station_map[key], value)
                    
                    entry.save()
                    
                    if include_arrests_and_staff:
                        other_location = Location.get_or_create_other_location(station)
                        try:
                            entry = LocationStatistics.objects.get(location=other_location, year_month=year_month)
                        except ObjectDoesNotExist:
                            entry = LocationStatistics()
                            entry.location = other_location
                            entry.year_month = year_month
                        
                        modified = False
                        for key in self.location_map.keys():
                            if key + year_month_csv in row:
                                value = row[key + year_month_csv]
                                value = value.replace(',','')
                                if value != '':
                                    setattr(entry, self.location_map[key], value)
                                    modified = True
                        if modified:
                                entry.save()
                        
                        general_staff = Staff.get_or_create_general_staff(station)
                        try:
                            entry = LocationStaff.objects.get(location=other_location, staff=general_staff, year_month=year_month)
                        except ObjectDoesNotExist:
                            entry = LocationStaff()
                            entry.location = other_location
                            entry.staff = general_staff
                            entry.year_month = year_month
                        
                        modified = False
                        for key in self.staff_map.keys():
                            if key + year_month_csv in row:
                                value = row[key + year_month_csv]
                                value = value.replace(',','')
                                if value != '':
                                    setattr(entry, self.staff_map[key], value)
                                    modified = True
                        if modified:
                                entry.save()
                    
                    month += 1
                    if month > 12:
                        year += 1
                        month = 1
                
                
                
            
            