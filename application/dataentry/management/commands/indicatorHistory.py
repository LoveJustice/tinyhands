import csv
import datetime

from django.core.management.base import BaseCommand

from dataentry.models import Country, IndicatorHistory

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Remove eisting indicator history if present and calculate indicators for all countries',
        )
        
    def handle(self, *args, **options):
        now = datetime.datetime.now()
        if now.month == 1:
            end_year = now.year - 1
            end_month = 12
        else:
            end_year = now.year
            end_month = now.month - 1
        
        if options['all']:
            print ('Calculating idicators for all countries from 2017-9 through ' + str(end_year) + '-' + str(end_month))
            IndicatorHistory.objects.all().delete()
            start_year = 2017
            start_month = 9
            always_store_indicators = False
        else:
            print ('Calculating idicators for all countries for the month ' + str(end_year) + '-' + str(end_month))
            IndicatorHistory.objects.filter(year=end_year, month=end_month).delete()
            start_year = end_year
            start_month = end_month
            always_store_indicators = True

        countries = Country.objects.all()
        
        for country in countries:
            found_indicators = always_store_indicators
            for year in range(start_year, end_year+1):
                if year == start_year:
                    first_month = start_month
                else:
                    first_month = 1
                    
                if year == end_year:
                    last_month = end_month
                else:
                    last_month = 12
                
                for month in range(first_month, last_month+1):
                    start_date = datetime.date(year, month, 1)
                    if month == 12:
                        end_date = datetime.date(year+1, 1, 1) - datetime.timedelta(1)
                    else:
                        end_date = datetime.date(year, month+1, 1) - datetime.timedelta(1)
                    results = IndicatorHistory.calculate_indicators(start_date, end_date, country)
                    if (not found_indicators and
                        ('irfCount' not in results or results['irfCount'] ==0) and
                        ('cifCount' not in results or results['cifCount'] ==0) and
                        ('vdfCount' not in results or results['vdfCount'] ==0) and
                        ('photosCount' not in results or results['photosCount'] ==0)):
                        continue
                    #print (country.name, start_date, end_date, results)
                    found_indicators = True
                    
                    indicator = IndicatorHistory()
                    indicator.country = country
                    indicator.year = year
                    indicator.month = month
                    indicator.indicators = results
                    indicator.save()
                    
        
        