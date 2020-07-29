import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.apps import apps

from budget.models import BorderStationBudgetCalculation
from dataentry.models import BorderStation, CifCommon, Country, CountryExchange, IntercepteeCommon, LocationStatistics, StationStatistics
from static_border_stations.models import Location

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--year',
            action='append',
            type=int,
        )
        parser.add_argument(
            '--month',
            action='append',
            type=int,
        )
        
    def location_tag(self, station, name):
        return station.station_code + "_" + name.lower()

        
    def handle(self, *args, **options):
        current_date = datetime.datetime.now()
        
        if options['year'] and options['month']:
            year = options['year'][0]
            month = options['month'][0]
        else:
            month = current_date.month
            year = current_date.year
            if (current_date.day < 6):
                month -= 2
            else:
                month -= 1
            if month < 1:
                month = 12 + month
                year -= 1
        
        if month > 11:
            end_date = str(year+1) + '-01-05'
        else:
            end_date = str(year) + '-' + str(month+1) + '-05'
        
        start_date = str(year) + '-' + str(month) + '-06'
        
        last_country = None
            
        year_month = year * 100 + month
        
        if month == 1:
            prior_year_month = (year - 1)*100 + 12
        else:
            prior_year_month = year_month - 1
        
        # create exchange rate entries
        countries = Country.objects.all()
        for country in countries:
            try:
                exchange = CountryExchange.objects.get(country=country, year_month=year_month)
            except ObjectDoesNotExist:
                exchange = CountryExchange()
                exchange.country = country
                exchange.year_month = year_month
            
            try:
                prior = CountryExchange.objects.get(country=country, year_month=prior_year_month)
                exchange.exchange_rate = prior.exchange_rate
            except ObjectDoesNotExist:
                exchange.exchange_rate = 1.0
            
            exchange.save()
            
        
        location_map = {}
        for location_statistics in LocationStatistics.objects.filter(year_month=year_month):
            if location_statistics.location is not None:
                location_tag = self.location_tag(location_statistics.station, location_statistics.location.name)
            else:
                location_tag = self.location_tag(location_statistics.station, '_other')
            location_statistics.intercepts = 0
            location_map[location_tag] = location_statistics
        
        intercepts = IntercepteeCommon.objects.filter(
                person__role = 'PVOT',
                interception_record__logbook_second_verification_date__gte=start_date,
                interception_record__logbook_second_verification_date__lte=end_date
                )
        for intercept in intercepts:
            location_tag = self.location_tag(intercept.interception_record.station, intercept.interception_record.location)
            if location_tag not in location_map:
                try:
                    location = Location.objects.get(border_station=intercept.interception_record.station, name__iexact=intercept.interception_record.location)
                    location_statistics = LocationStatistics()
                    location_statistics.year_month = year_month
                    location_statistics.location = location
                    location_statistics.station = intercept.interception_record.station
                    location_statistics.intercepts = 0
                    location_map[location_tag] = location_statistics
                except ObjectDoesNotExist: 
                    location_tag = self.location_tag(intercept.interception_record.station, '_other')
                    if location_tag not in location_map:
                        location_statistics = LocationStatistics()
                        location_statistics.year_month = year_month
                        location_statistics.location = None
                        location_statistics.station = intercept.interception_record.station
                        location_statistics.intercepts = 0
                        location_map[location_tag] = location_statistics
                
            location_map[location_tag].intercepts += 1
        
        for location_tag in location_map.keys():
            location_map[location_tag].save()
        
        border_stations = BorderStation.objects.all().order_by('operating_country')
        for station in border_stations:
            try:
                entry = StationStatistics.objects.get(year_month=year_month, station=station)
            except ObjectDoesNotExist:
                entry = StationStatistics()
                entry.year_month = year_month
                entry.station = station
                entry.save()
            
            # Collections
            # Budget
            try:
                budget = BorderStationBudgetCalculation.objects.get(border_station=station, month_year__year=year, month_year__month=month)
                entry.budget = budget.station_total()
            except ObjectDoesNotExist:
                pass
            
            # gospel
            # empowerment
            
            # cif count 
            entry.cifs = CifCommon.objects.filter(
                logbook_submitted__gte=start_date,
                logbook_submitted__lte=end_date,
                station=station).count()
            
            # convictions
            
            entry.save()
        