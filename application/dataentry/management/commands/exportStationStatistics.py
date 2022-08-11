import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.apps import apps

from export_import.google_sheet_basic import GoogleSheetBasic
from dataentry.models import BorderStation, Country, CountryExchange, IntercepteeCommon, LocationStaff, LocationStatistics, StationStatistics
from static_border_stations.models import Location

class Command(BaseCommand):
    def handle(self, *args, **options):
        spreadsheet = 'Station Statistics' + settings.SPREADSHEET_SUFFIX
        sheet = GoogleSheetBasic(spreadsheet,'Statistics')
        new_rows = Command.export_statistics()
        old_count = sheet.rowCount
        
        reqs = []
        reqs.append(sheet.expand_request(len(new_rows)))
        reqs.append(sheet.delete_request(0, old_count))
        sheet.batch_update(reqs)
        
        sheet.append_rows(new_rows)
    
    @staticmethod
    def export_statistics():
        current_date = datetime.datetime.now()
        end_month = current_date.month
        end_year = current_date.year
        end_month -= 1
        if end_month < 1:
            end_month = 12 + month
            end_year -= 1
        
        end_year_month = end_year * 100 + end_month
        results = [[
                'Station Code','Country',
                'Last Month Staff', 'Last Month Intercepts', 'Last Month Arrests', 'Last Month Budget','Last Month Gospel', 'Last Month Empowerment', 
                'Last 6 Months Staff', 'Last 6 Months Intercepts', 'Last 6 Months Arrests', 'Last 6 Months Budget','Last 6 Months Gospel', 'Last 6 Months Empowerment', 
                'Fiscal Year Staff', 'Fiscal Year Intercepts', 'Fiscal Year Arrests', 'Fiscal Year Budget','Fiscal Year Gospel', 'Fiscal Year Empowerment', 
                'All Time Staff', 'All Time Intercepts', 'All Time Arrests', 'All Time Budget','All Time Gospel', 'All Time Empowerment', 
                
            ]
            ]
        stations = BorderStation.objects.all().order_by('operating_country__name','station_code')
        for station in stations:
            station_data = []
            station_data.append(station.station_code)
            station_data.append(station.operating_country.name)
            
            #Last month
            Command.process_statistics(station_data, station, 'last month', end_year_month, end_year_month)
            
            #Last 6 months
            if end_month < 6:
                start_year_month = (end_year - 1) * 100 + 7 + end_month
            else:
                start_year_month = end_year * 100 + end_month - 5          
            Command.process_statistics(station_data, station, 'last 6 months', start_year_month, end_year_month)
            
            #Fiscal Year
            if end_month >= 10:
                start_year_month = end_year * 100 + 10
            else:
                start_year_month = (end_year - 1) * 100 + 10
            Command.process_statistics(station_data, station, 'Fiscal year', start_year_month, end_year_month)
            
            #all time
            Command.process_statistics(station_data, station, 'All time', None, None)
            results.append(station_data)
        
        return results
    
    def apply_exchange_rate(value, country, year_month):
        try:
            exchange = CountryExchange.objects.get(country=country, year_month=year_month)
            rate = exchange.exchange_rate
        except ObjectDoesNotExist:
            rate = 1.0
        
        if value is not None:
            value = int(value * 100 / rate)/100
        
        return value
    
    @staticmethod   
    def process_statistics (station_data, station, prefix, start, end):
        if start is None:
            statistics = StationStatistics.objects.filter(station=station)
        else:
            statistics = StationStatistics.objects.filter(station=station, year_month__gte=start, year_month__lte=end)
        
        gospel = 0
        empowerment = 0
        budget = 0
        for statistic in statistics:
            if statistic.gospel is not None:
                gospel += statistic.gospel
            if statistic.empowerment is not None:
                empowerment += statistic.empowerment
            if statistic.budget is not None:
                budget += Command.apply_exchange_rate(statistic.budget, station.operating_country, statistic.year_month)
        
        
        if start is None:
            sum_location = LocationStatistics.objects.filter(location__border_station=station).aggregate(Sum('intercepts'), Sum('arrests'))
            sum_staff = LocationStaff.objects.filter(location__border_station=station).aggregate(Sum('work_fraction')) 
        else:
            sum_location = LocationStatistics.objects.filter(location__border_station=station, year_month__gte=start, year_month__lte=end).aggregate(Sum('intercepts'), Sum('arrests'))
            sum_staff = LocationStaff.objects.filter(location__border_station=station, year_month__gte=start, year_month__lte=end).aggregate(Sum('work_fraction'))
        if sum_staff['work_fraction__sum'] is None:
            station_data.append(0)
        else:
            station_data.append(sum_staff['work_fraction__sum'])
        if sum_location['intercepts__sum'] is None:
            station_data.append(0)
        else:
            station_data.append(sum_location['intercepts__sum'])
        if sum_location['arrests__sum'] is None:
            station_data.append(0)
        else:
            station_data.append(sum_location['arrests__sum'])
        station_data.append(budget)
        station_data.append(gospel)
        station_data.append(empowerment)
        
        
        
            
            
                
            
                