import datetime
import dateutil.parser
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.models import Sum
from django.core.exceptions import ObjectDoesNotExist
import time

from export_import.google_sheet import GoogleSheet
from dataentry.models import *
from static_border_stations.models import Location

def fmt(value):
    if value is None:
        return ''
    else:
        return value

def get_station_stats_export_rows(objs):
    enter = datetime.datetime.now()
    key = objs[0]['key']
    year_month = objs[0]['year_month']
    
    station_stats_headers = ['Key', 'Station', 'Station Code', 'Category', 'Country', 'Year Month', 'Convictions', 'Empowerment', 'Budget', 'gospel', '#Active Monitoring Locations', '#Active Shelters', 'Committee']
    location_stats_headers = ['Intercepts', 'Arrests', 'Evidence Intercepts','High Risk Intercepts', 'Invalid Intercepts']
    location_staff_headers = ['Staff']
    monthly_report_headers = ['SMR']
    country_exchange_headers = ['Exchange Rate']
    headers = station_stats_headers + location_stats_headers + location_staff_headers + monthly_report_headers + country_exchange_headers
    
    rows = []
    rows.append(headers)
    
    station_stats_list = StationStatistics.objects.filter(year_month=year_month)
    
    for station_stats in station_stats_list:
        work_days = 21
        row = []
        row.append(key)
        row.append(fmt(station_stats.station.station_name))
        row.append(fmt(station_stats.station.station_code))
        try:
            category_name = station_stats.station.project_category.name
        except:
            category_name = ''
        row.append(fmt(category_name))
        row.append(fmt(station_stats.station.operating_country.name))
        row.append(fmt(station_stats.year_month))
        row.append(fmt(station_stats.convictions))
        row.append(fmt(station_stats.empowerment))
        row.append(fmt(station_stats.budget))
        row.append(fmt(station_stats.gospel))
        row.append(fmt(station_stats.active_monitor_locations))
        row.append(fmt(station_stats.active_shelters))
        row.append(fmt(station_stats.subcommittee_members))
        work_days = station_stats.work_days
        if work_days is None or work_days == 0:
            work_days = 21
    
   
        sums = LocationStatistics.objects.filter(location__border_station__id = station_stats.station.id, year_month = year_month).aggregate(
            Sum('intercepts'), Sum('arrests'), Sum('intercepts_evidence'), Sum('intercepts_high_risk'),Sum('intercepts_invalid'))
        row.append(fmt(sums['intercepts__sum']))
        row.append(fmt(sums['arrests__sum']))
        row.append(fmt(sums['intercepts_evidence__sum']))
        row.append(fmt(sums['intercepts_high_risk__sum']))
        row.append(fmt(sums['intercepts_invalid__sum']))
    
    
        sums = LocationStaff.objects.filter(location__border_station__id = station_stats.station.id, year_month = year_month).aggregate(Sum('work_fraction'))
        if sums['work_fraction__sum'] is not None:
            row.append(fmt(sums['work_fraction__sum']/work_days))
        else:
            row.append('')
    
        try:
            monthly_report = MonthlyReport.objects.get(station__id=station_stats.station.id, year = year_month//100, month=year_month%100)
            row.append(fmt(monthly_report.average_points))
        except ObjectDoesNotExist:
            row.append('')
    
        try:
            exchange = CountryExchange.objects.get(year_month=year_month, country=station_stats.station.operating_country)
            row.append(exchange.exchange_rate)
        except:
            row.append('');
    
        rows.append(row)
        
    return rows


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--init_settings',
            action='append',
            help='Initialize site settings value that contains last time exported',
        )
    
    def handle(self, *args, **options):
        start = datetime.datetime.now()
        site_setting_name = 'station_statistics_export'
        run_time = datetime.datetime.now()
        print ('starting at ' + run_time.isoformat())
        spreadsheet = 'Station Stats' + settings.SPREADSHEET_SUFFIX
        sheet = GoogleSheet(spreadsheet,'Stats', 'Key', get_station_stats_export_rows)
        
        site_settings = SiteSettings.objects.all()[0]
        
        if options['init_settings']:
            try:
                setting = site_settings.get_setting_by_name(site_setting_name)
                site_settings.set_setting_value_by_name(site_setting_name, run_time.isoformat())
            except:
                site_settings.data.append({'name':site_setting_name, 'value':run_time.isoformat(), 'description':'Last time station statistics were exported'})
            site_settings.save()
            return
        
        try:
            date_str = site_settings.get_setting_value_by_name(site_setting_name)
            last_exported = dateutil.parser.parse(date_str + ' Z')
        except:
            print ('Unable to find value for site setting(' + site_setting_name + ') for the last time the export was done')
            return
        print ('last exported time', date_str)
        
         
        to_process = {}
         
        station_stats_headers = ['Key', 'Station', 'Station Code', 'Country', 'Year Month', 'Convictions', 'Empowerment', 'Budget', 'SMR']
        location_stats_headers = ['Intercepts', 'Arrests', 'Evidence Intercepts','High Risk Intercepts', 'Invalid Intercepts']
        location_staff_headers = ['Staff']
        station_headers = ['#Active Monitoring Locations']
        headers = station_stats_headers + location_stats_headers + location_staff_headers + station_headers
        
        exchange_list = CountryExchange.objects.filter(date_time_last_updated__gte = last_exported).order_by('year_month')
        for entry in exchange_list:
            if entry.year_month not in to_process:
                to_process[entry.year_month] = True
        
        station_stats = StationStatistics.objects.filter(modified_date__gte = last_exported)
        for entry in station_stats:
            if entry.year_month not in to_process:
               to_process[entry.year_month] = True
        
        location_stats = LocationStatistics.objects.filter(modified_date__gte = last_exported)
        for entry in location_stats:
            if entry.year_month not in to_process:
               to_process[entry.year_month] = True
         
        location_staff = LocationStaff.objects.filter(modified_date__gte = last_exported)
        for entry in location_staff:
            if entry.year_month not in to_process:
               to_process[entry.year_month] = True
        
        time.sleep(5)
        for year_month in to_process.keys():
            print('exporting year_month:', year_month)
            key = str(year_month)
            sheet.update(key, {'key':key, 'year_month':year_month})
            time.sleep(5)
        
        site_settings.set_setting_value_by_name(site_setting_name, run_time.isoformat())
        site_settings.save()
                
        
        
        
         