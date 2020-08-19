import csv
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.db.models import Sum

from dataentry.models import BorderStation, StationStatistics, LocationStatistics, LocationStaff
from static_border_stations.models import Location, Staff

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('mode', nargs='+', type=str)
        parser.add_argument('filename', nargs='+', type=str)
        parser.add_argument('startYearMonth', nargs='+', type=int)
        parser.add_argument('endYearMonth', nargs='+', type=int)
        parser.add_argument('--fix', action='append', type=str)
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
        
        fixes = {
            'mapping': {},
            'new_location': [],
            'rename': {},
            'not_monitoring': {}
            }
        if options['fix']:
            self.process_fixes(options['fix'][0], fixes)
        
        if (mode == 'station_pre'):
            self.process_station_statistics(file_name, start_year, start_month, end_year, end_month, True)
        elif (mode == 'station_post'):
            self.process_station_statistics(file_name, start_year, start_month, end_year, end_month, False)
        elif (mode == 'location'):
            self.processLocationStatistics(file_name, start_year, start_month, end_year, end_month, fixes['mapping'])
        elif (mode == 'arrest'):
            self.processArrests(file_name)
    
    def process_fixes(self, fix_file, fixes):
        with open(fix_file) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['Station1']  != '':
                    if row['New Location'] == 'TRUE':
                        fixes['new_location'].append({'station':row['Station1'], 'location':row['Location']})
                    elif row['Matching SL Name'] == '':
                        print('__Other for', row['Location'])
                        fixes['mapping'][row['Location']] = "__Other"
                    else:
                        fixes['mapping'][row['Location']] = row['Matching SL Name']
                
                if row['New Location Name'] != '':
                    fixes['rename'][row['Current Location']] = {'station':row['Station2'], 'new_location':row['New Location Name']}
                
                if row['Currently Monitoring'] == 'FALSE':
                    fixes['not_monitoring'][row['Current Location']] = row['Station2']
            
            for new_location in fixes['new_location']:
                try:
                    existing = Location.objects.get(border_station__station_name=new_location['station'], name=new_location['location'])
                    print('location', new_location['location'], 'already exists for station', new_location['station'])
                except ObjectDoesNotExist:
                    location = Location()
                    print('new_location, border_station', new_location['station'])
                    location.border_station = BorderStation.objects.get(station_name=new_location['station'])
                    location.name = new_location['location']
                    location.save()
            
            for key, value in fixes['rename'].items():
                try:
                    location = Location.objects.get(border_station__station_name=value['station'], name=key)
                    location.name = value['new_location']
                    location.save()
                except ObjectDoesNotExist:
                    print('rename location', key, value, 'not found')
            
            for key, value in fixes['not_monitoring'].items():
                try:
                    location = Location.objects.get(border_station__station_name = value, name=key)
                except ObjectDoesNotExist:
                    print ('Unable to find location for station',value,'location', key)
                
                location.active = False
                location.save()
            
            for key, value in fixes['mapping'].items():
                if value in fixes['rename']:
                    fixes['mapping'][key] = fixes['rename'][value]['new_location']
                    
            #print("MAPPING", fixes['mapping'])
                    
                    
    def processLocationStatistics(self, file_name, start_year, start_month, end_year, end_month, mapping):
        skip = False
        with open(file_name) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                tmp_station_code = row['Station Code']
                tmp_location = row['Location'].strip()
                if tmp_location in mapping:
                    tmp_location = mapping[tmp_location]
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
                    if tmp_location == '__Other':
                        location = Location.get_or_create_other_location(station)
                    else:
                        location = Location.objects.get(border_station=station, name__iexact=tmp_location)
                except ObjectDoesNotExist:
                    print('Unable to find location with name', '"' + tmp_location + '"')
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
                    for key in ['Int']:
                        if key + year_month_csv in row:
                            value = row[key + year_month_csv]
                            value = value.replace(',','')
                            old_value = getattr(entry, self.location_map[key])
                            if old_value is None:
                                old_value = 0
                            if value != '':
                                setattr(entry, self.location_map[key], old_value + int(value))
                                #print (station.station_code, location.name, key + year_month_csv, old_value, value, entry.id)
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
                        
                        
    def process_station_statistics(self, file_name, start_year, start_month, end_year, end_month, include_arrests_and_staff):
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
                        for key in ['Int']:
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
    
    def processArrest(self, station_name, arrest_date, results):
        try:
            arrest_parts = arrest_date.split('/')
            year_month = 100 * int(arrest_parts[2]) + int(arrest_parts[0])
        except:
            print ('failed to get year_month. Station', station_name, 'date', arrest_date)
            return
        
        if station_name not in results:
            results[station_name] = {}
        
        if year_month in results[station_name]:
            results[station_name][year_month] += 1
        else:
            results[station_name][year_month] = 1
        
    def processArrests (self, file_name):
        results = {}
        with open(file_name) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['Closed Station'] != '' and row['Closed Arrested'] != '':
                    self.processArrest(row['Closed Station'], row['Closed Arrested'], results)
                
                if row['Inactive Station'] != '' and row['Inactive Arrested'] != '':
                    self.processArrest(row['Inactive Station'], row['Inactive Arrested'], results)
                
                if row['Active Station'] != '' and row['Active Arrested'] != '':
                    self.processArrest(row['Active Station'], row['Active Arrested'], results)
        
        for key in results.keys():
            try:
                station = BorderStation.objects.get(station_name=key)
            except ObjectDoesNotExist:
                print ("Unable to find station with name", key)
                continue
            
            for year_month in results[key].keys():
                location_total = LocationStatistics.objects.filter(location__border_station=station, year_month=year_month).aggregate(Sum('arrests'))['arrests__sum']
                if location_total is None:
                    location_total = 0
                
                if location_total > results[key][year_month]:
                    print (key, year_month, location_total, results[key][year_month], "********")
                else:
                    print (key, year_month, location_total, results[key][year_month])
                    