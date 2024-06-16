import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db.models import Count

from budget.models import BorderStationBudgetCalculation
from dataentry.models import BorderStation, CifCommon, Country, CountryExchange, Gospel, GospelVerification, IntercepteeCommon, LegalCaseSuspect, LocationStatistics, StationStatistics
from legal.models import LegalChargeSuspect
from static_border_stations.models import  CommitteeMember, Location

ARREST_VERIFICATION_START = '2024-07-01'

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
            
            if exchange.exchange_rate is None or exchange.exchange_rate == 1.0:
                try:
                    prior = CountryExchange.objects.get(country=country, year_month=prior_year_month)
                    exchange.exchange_rate = prior.exchange_rate
                except ObjectDoesNotExist:
                    exchange.exchange_rate = 1.0
            
            exchange.save()
        
        # make sure location statistics exists for each active location
        locations = Location.objects.all()
        for location in locations:
            if location.border_station is not None and 'hasProjectStats' in location.border_station.features:
                try:
                    location_statistics = LocationStatistics.objects.get(location=location, year_month=year_month)
                except ObjectDoesNotExist:
                    if not location.active:
                        # Not an active location and no existing entry - skip location
                        continue
                    location_statistics = LocationStatistics()
                    location_statistics.location = location
                    location_statistics.year_month = year_month
                
                location_statistics.intercepts = 0
                location_statistics.intercepts_evidence = 0
                location_statistics.intercepts_high_risk = 0
                location_statistics.intercepts_invalid = 0
                country = location_statistics.location.border_station.operating_country
                if 'legal_arrest_and_conviction' in country.options and country.options['legal_arrest_and_conviction']:
                    location_statistics.arrests = 0
                location_statistics.save()
        
        intercepts = IntercepteeCommon.objects.filter(
                person__role = 'PVOT',
                interception_record__verified_date__gte=start_date,
                interception_record__verified_date__lt=end_date,
                interception_record__date_of_interception__gte='2020-10-01'
                )
        for intercept in intercepts:
            country = intercept.interception_record.station.operating_country
            try:
                location = Location.objects.get(border_station=intercept.interception_record.station, name__iexact=intercept.interception_record.location)
            except ObjectDoesNotExist:
                location = Location.get_or_create_other_location(intercept.interception_record.station)
            
            try:
                location_statistics = LocationStatistics.objects.get(location=location, year_month = year_month)
                if location_statistics.intercepts is None:
                    location_statistics.intercepts = 0
                if location_statistics.intercepts_evidence is None:
                    location_statistics.intercepts_evidence = 0
                if location_statistics.intercepts_high_risk is None:
                    location_statistics.intercepts_high_risk = 0
                if location_statistics.intercepts_invalid is None:
                    location_statistics.intercepts_invalid = 0
            except ObjectDoesNotExist:
                location_statistics = LocationStatistics()
                location_statistics.year_month = year_month
                location_statistics.location = location
                location_statistics.intercepts = 0
                location_statistics.intercepts_evidence = 0
                location_statistics.intercepts_high_risk = 0
                location_statistics.intercepts_invalid = 0
                if 'legal_arrest_and_conviction' in country.options and country.options['legal_arrest_and_conviction']:
                    location_statistics.arrests = 0
            
            
            if intercept.interception_record.verified_evidence_categorization.startswith('Evidence'):
                location_statistics.intercepts_evidence += 1
            elif intercept.interception_record.verified_evidence_categorization.startswith('High'):
                location_statistics.intercepts_high_risk += 1
            elif intercept.interception_record.verified_evidence_categorization.startswith('Should not'):
                location_statistics.intercepts_invalid += 1
            location_statistics.intercepts = location_statistics.intercepts_evidence + location_statistics.intercepts_high_risk
            location_statistics.save()
        
        for country in countries:
            if 'legal_arrest_and_conviction' in country.options and country.options['legal_arrest_and_conviction']:
                # Count arrests
                if start_date >= ARREST_VERIFICATION_START:
                    suspects = LegalChargeSuspect.objects.filter(
                            legal_charge__station__operating_country=country,
                            verified_date__gte=start_date,
                            verified_date__lt=end_date,
                            arrest_submitted_date__gte=ARREST_VERIFICATION_START
                        )
                    for suspect in suspects:
                        try:
                            location = Location.objects.get(border_station=suspect.legal_charge.station, name__iexact=suspect.legal_charge.location)
                        except:
                            location = Location.get_or_create_other_location(suspect.legal_charge.station)
                            
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
                            location_statistics.arrests = 0
                        
                        location_statistics.arrests += 1
                        location_statistics.save()
                else:
                    suspects = LegalCaseSuspect.objects.filter(
                            legal_case__station__operating_country=country, arrest_submitted_date__gte=start_date, arrest_submitted_date__lt=end_date)
                    for suspect in suspects:
                        try:
                            location = Location.objects.get(border_station=suspect.legal_case.station, name__iexact=suspect.legal_case.location)
                        except ObjectDoesNotExist:
                            location = Location.get_or_create_other_location(suspect.legal_case.station)
                        
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
                            location_statistics.arrests = 0
                        
                        location_statistics.arrests += 1
                        location_statistics.save()
        
        border_stations = BorderStation.objects.all().order_by('operating_country')
        for station in border_stations:
            country = station.operating_country
            try:
                entry = StationStatistics.objects.get(year_month=year_month, station=station)
            except ObjectDoesNotExist:
                entry = StationStatistics()
                entry.year_month = year_month
                entry.station = station
                entry.save()
            
            if entry.subcommittee_members is None:
                entry.subcommittee_members = CommitteeMember.objects.filter(border_station = station).count()
            if entry.active_monitor_locations is None:
                locations = Location.objects.filter(border_station = station, location_type = 'monitoring', active = True)
                entry.active_monitor_locations = len(locations)
            if entry.active_shelters is None:
                shelters = Location.objects.filter(border_station = station, location_type = 'shelter', active = True)
                entry.active_shelters = len(shelters)
            if 'legal_arrest_and_conviction' in country.options and country.options['legal_arrest_and_conviction'] and entry.convictions is None:
                entry.convictions = 0
            
            # Budget
            """
            try:
                budget = BorderStationBudgetCalculation.objects.get(border_station=station, month_year__year=year, month_year__month=month)
                if entry.budget is None:
                    entry.budget = budget.station_total()
            except ObjectDoesNotExist:
                pass
            """
            
            # gospel
            entry.gospel = (GospelVerification.objects.filter(vdf__station=station,
                                                            form_changes = 'No',
                                                            date_of_followup__gte=start_date,
                                                            date_of_followup__lt=end_date).count() +
                            Gospel.objects.filter(station=station,
                                                            date_time_entered_into_system__gte=start_date,
                                                            date_time_entered_into_system__lt=end_date).count())
            
            # empowerment
            if 'legal_arrest_and_conviction' in country.options and country.options['legal_arrest_and_conviction']:
                # Count convictions
                entry.convictions = LegalCaseSuspect.objects.filter(
                        verdict='Conviction',
                        legal_case__station = station,
                        verdict_submitted_date__gte=start_date,
                        verdict_submitted_date__lt=end_date
                    ).count()
            
            # cif count 
            
            entry.save()
            
            
        