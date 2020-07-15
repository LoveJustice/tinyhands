import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.apps import apps

from budget.models import BorderStationBudgetCalculation
from dataentry.models import BorderStation, CifCommon, IntercepteeCommon, OperationsData




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
        border_stations = BorderStation.objects.all().order_by('operating_country')
        for station in border_stations:
            try:
                entry = OperationsData.objects.get(year_month=year_month, station=station)
            except ObjectDoesNotExist:
                entry = OperationsData()
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
            
            # interceptions
            entry.intercepts = IntercepteeCommon.objects.filter(
                person__role = 'PVOT',
                interception_record__logbook_second_verification_date__gte=start_date,
                interception_record__logbook_second_verification_date__lte=end_date,
                interception_record__station=station
                ).count()
            
            # arrests
            # gospel
            # empowerment
            
            # cif count 
            entry.cifs = CifCommon.objects.filter(
                logbook_submitted__gte=start_date,
                logbook_submitted__lte=end_date,
                station=station).count()
            
            # convictions
            
            entry.save()
        