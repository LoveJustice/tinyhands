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
        
    def handle(self, *args, **options):
        current_date = datetime.datetime.now()
        
        if options['year'] and options['month']:
            year = options['year'][0]
            month = options['month'][0]
        else:
            month = current_date.month
            year = current_date.year
            month -= 1
            if month < 1:
                month = 12 + month
                year -= 1
        
        if month > 11:
            end_date = str(year+1) + '-01-01'
        else:
            end_date = str(year) + '-' + str(month+1) + '-01'
        
        start_date = str(year) + '-' + str(month) + '-01'
        
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
            
        for location_statistics in LocationStatistics.objects.filter(year_month=year_month):
            location_statistics.intercepts = 0
            location_statistics.intercepts_evidence = 0
            location_statistics.intercepts_high_risk = 0
            location_statistics.intercepts_invalid = 0
            location_statistics.save()
        
        intercepts = IntercepteeCommon.objects.filter(
                person__role = 'PVOT',
                interception_record__logbook_second_verification_date__gte=start_date,
                interception_record__logbook_second_verification_date__lt=end_date
                )
        for intercept in intercepts:
            try:
                location = Location.objects.get(border_station=intercept.interception_record.station, name__iexact=intercept.interception_record.location)
            except ObjectDoesNotExist:
                location = Location.get_or_create_other_location(intercept.interception_record.station)
            
            try:
                location_statistics = LocationStatistics.objects.get(location=location, year_month = year_month)
            except ObjectDoesNotExist:
                location_statistics = LocationStatistics()
                location_statistics.year_month = year_month
                location_statistics.location = location
                location_statistics.intercepts = 0
                location_statistics.intercepts_evidence = 0
                location_statistics.intercepts_high_risk = 0
                location_statistics.intercepts_invalid = 0
            
            location_statistics.intercepts += 1
            if intercept.interception_record.logbook_second_verification.startswith('Evidence'):
                location_statistics.intercepts_evidence += 1
            elif intercept.interception_record.logbook_second_verification.startswith('High'):
                location_statistics.intercepts_high_risk += 1
            elif intercept.interception_record.logbook_second_verification.startswith('Should not'):
                location_statistics.intercepts_invalid += 1
            location_statistics.save() 
        
        border_stations = BorderStation.objects.all().order_by('operating_country')
        for station in border_stations:
            try:
                entry = StationStatistics.objects.get(year_month=year_month, station=station)
            except ObjectDoesNotExist:
                entry = StationStatistics()
                entry.year_month = year_month
                entry.station = station
                locations = Location.objects.filter(border_station = station, location_type = 'monitoring', active = True)
                entry.active_monitor_locations = len(locations)
                entry.save()
            
            # Collections
            # Budget
            try:
                budget = BorderStationBudgetCalculation.objects.get(border_station=station, month_year__year=year, month_year__month=month)
                entry.budget = budget.station_total() + budget.past_month_sent_total()
            except ObjectDoesNotExist:
                pass
            
            # gospel
            # empowerment
            
            # cif count 
            
            
            # convictions
            
            entry.save()
        