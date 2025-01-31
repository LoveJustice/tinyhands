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
        parser.add_argument('--include', action='append', type=str)
        parser.add_argument('--fix', action='append', type=str)
        parser.add_argument('--country', action='append', type=str)
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
        
        if mode == 'station' or mode == 'location':
            if not options['include']:
                print('Must define included values for station or location mode')
                return
            
            to_include = {'Ast':False, 'Int':False,'Staff':False}
            includes = options['include'][0].split(',')
            for include in includes:
                if include == '':
                    continue
                if include not in to_include:
                    print ('Unknown included value type ', include)
                    return
                to_include[include] = True
        
        if (mode == 'station'):
            self.process_station_statistics(file_name, start_year, start_month, end_year, end_month, to_include)
        elif (mode == 'location'):
            self.processLocationStatistics(file_name, start_year, start_month, end_year, end_month, fixes['mapping'], to_include)
        elif (mode == 'arrest'):
            self.processArrests(file_name, start_year, start_month, end_year, end_month, options['country'][0])
    
    def reset_location_data(self, station, year_month, to_include):
        location_statistics = LocationStatistics.objects.filter(location__border_station=station, year_month=year_month)
        for location_statistic in location_statistics:
            modified = False
            for key in self.location_map.keys():
                if key in to_include and to_include[key] and getattr(location_statistic, self.location_map[key], None) is not None:
                    setattr(location_statistic, self.location_map[key], None)
                    modified = True
            
            if modified:
                location_statistic.save()
    
    def reset_location_staff(self, station, year_month, to_include):
        location_staff_list = LocationStaff.objects.filter(location__border_station=station, year_month=year_month)
        for location_staff in location_staff_list:
            modified = False
            for key in self.staff_map.keys():
                if key in to_include and to_include[key] and getattr(location_staff, self.staff_map[key], None) is not None:
                    setattr(location_staff, self.staff_map[key], None)
                    modified = True
            
            if modified:
                location_staff.save()
    
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
                    
                    
    def processLocationStatistics(self, file_name, start_year, start_month, end_year, end_month, mapping, to_include):
        process_location_statistics = False
        for key in self.location_map.keys():
            if key in to_include and to_include[key]:
                process_location_statistics = True
        
        process_location_staff = False
        for key in self.staff_map.keys():
            if key in to_include and to_include[key]:
                process_location_staff = True
                
        with open(file_name) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                tmp_station_code = row['Station Code']
                try:
                    station = BorderStation.objects.get(station_code=station_code)
                except:
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
                    
                    if process_location_statistics:
                        self.reset_location_data(station, year_month, to_include)
                    if process_location_staff:
                        self.reset_location_staff(station, year_month, to_include)
            
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
                    
                    if process_location_statistics:
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
                                old_value = getattr(entry, self.location_map[key])
                                if old_value is None:
                                    old_value = 0
                                if value != '':
                                    setattr(entry, self.location_map[key], old_value + int(value))
                                    #print (station.station_code, location.name, key + year_month_csv, old_value, value, entry.id)
                                    modified = True
                            
                        if modified:
                                entry.save()
                    if process_location_staff:
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
                        
                        
    def process_station_statistics(self, file_name, start_year, start_month, end_year, end_month, to_include):
        process_location_statistics = False
        for key in self.location_map.keys():
            if key in to_include and to_include[key]:
                process_location_statistics = True
        
        process_location_staff = False
        for key in self.staff_map.keys():
            if key in to_include and to_include[key]:
                process_location_staff = True
                
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
                    
                    if process_location_statistics:
                        self.reset_location_data (station, year_month, to_include)
                        
                        other_location = Location.get_or_create_other_location(station)
                        try:
                            entry = LocationStatistics.objects.get(location=other_location, year_month=year_month)
                        except ObjectDoesNotExist:
                            entry = LocationStatistics()
                            entry.location = other_location
                            entry.year_month = year_month
                        
                        modified = False
                        for key in self.location_map.keys():
                            #print (year_month, key, to_include[key], key + year_month_csv in row)
                            if to_include[key] and key + year_month_csv in row:
                                value = row[key + year_month_csv]
                                value = value.replace(',','')
                                if value != '':
                                    setattr(entry, self.location_map[key], value)
                                    modified = True
                            
                        if modified:
                                entry.save()
                    
                    if process_location_staff:
                        self.reset_location_staff(station, year_month, to_include)
                        
                        other_location = Location.get_or_create_other_location(station)
                        try:
                            entry = LocationStatistics.objects.get(location=other_location, year_month=year_month)
                        except ObjectDoesNotExist:
                            entry = LocationStatistics()
                            entry.location = other_location
                            entry.year_month = year_month
                        
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
                            if to_include[key] and key + year_month_csv in row:
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
        
    def processArrests (self, file_name, start_year, start_month, end_year, end_month, country):
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
        
        stations = BorderStation.objects.filter(operating_country__name=country)
        start_year_month = 100 * start_year + start_month
        for station in stations:
            year=start_year
            month = start_month
            year_month = 100 * year + month
            end_year_month = 100 * end_year + end_month
            if station.station_name in results:
                station_result = results[station.station_name]
                expected_total = 0
                for key in station_result.keys():
                    expected_total += station_result[key]
                    
            else:
                station_result = {}
                expected_total = 0
            other_location = Location.get_or_create_other_location(station)
            total = 0
           
            while year_month <= end_year_month:
                location_total = LocationStatistics.objects.filter(location__border_station=station, year_month=year_month).exclude(
                    location=other_location).aggregate(Sum('arrests'))['arrests__sum']
                if location_total is None:
                    location_total = 0
                
                if year_month in station_result:
                    result_total = station_result[year_month]
                    #print (station.station_name, 'result_total', year_month, result_total)
                    total += result_total
                else:
                    result_total = 0
                
                if location_total > result_total:
                    diff = result_total
                    entries = LocationStatistics.objects.filter(location__border_station=station, year_month=year_month)
                    for entry in entries:
                        entry.arrests = 0
                        entry.save()
                else:
                    diff = result_total - location_total
                
                if diff > 0:
                    try:
                        location_stats = LocationStatistics.objects.get(location=other_location, year_month=year_month)
                    except ObjectDoesNotExist:
                        location_stats = LocationStatistics()
                        location_stats.location = other_location
                        location_stats.year_month = year_month
                    location_stats.arrests = diff
                    location_stats.save()
                
                month += 1
                if month > 12:
                    month = 1
                    year += 1
                year_month = 100 * year + month
            
            print (station.station_name, expected_total, total)
            
            # Process arrests prior to the starting date
            for year_month in station_result.keys():
                if year_month < start_year_month:
                    try:
                        location_stats = LocationStatistics.objects.get(location=other_location, year_month=year_month)
                    except ObjectDoesNotExist:
                        location_stats = LocationStatistics()
                        location_stats.location = other_location
                        location_stats.year_month = year_month
                    location_stats.arrests = station_result[year_month]
                    total += station_result[year_month]
                    location_stats.save()
            
            print (station.station_name, expected_total, total, station_result)
            
