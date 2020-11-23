import logging
import datetime

from rest_framework import filters as fs
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Sum
from django.db import transaction
from dataentry.models import StationStatistics
from dataentry.serializers import StationStatisticsSerializer, LocationStaffSerializer, LocationStatisticsSerializer, CountryExchangeSerializer
from rest_api.authentication import HasPostPermission, HasPutPermission, HasDeletePermission

from dataentry.models import BorderStation, CifCommon, Country, CountryExchange, IrfCommon, LegalCaseSuspect, LocationStaff, LocationStatistics, StationStatistics, MonthlyReport, VdfCommon
from static_border_stations.models import Location, Staff

logger = logging.getLogger(__name__)

class StationStatisticsViewSet(viewsets.ModelViewSet):
    queryset = StationStatistics.objects.all()
    serializer_class = StationStatisticsSerializer
    permission_classes = (IsAuthenticated, )
    
    def retrieve_country_data(self, request, country_id, year_month):
        results = StationStatistics.objects.filter(station__operating_country__id=country_id, year_month=year_month).order_by('station__non_transit', 'station__station_name')
        
        serializer = StationStatisticsSerializer(results , many=True, context={'request': request})
        return Response(serializer.data)
    
    def update_station_data(self, request):
        station_id = request.data['station']
        year_month = request.data['year_month']
        budget = request.data['budget']
        gospel = request.data['gospel']
        empowerment = request.data['empowerment']
        station = BorderStation.objects.get(id=station_id)
        try:
            station_statistics = StationStatistics.objects.get(station=station, year_month=year_month)
        except ObjectDoesNotExist:
            station_statistics = StationStatistics()
            station_statistics.station = station
            station_statistics.year_month = year_month
            
        station_statistics.budget = budget
        station_statistics.gospel = gospel
        station_statistics.empowerment = empowerment
        if not station.operating_country.enable_all_locations:
            # if enable_all_lcoations is not true, then the staff and arrests can be updated here
            other_location = Location.get_or_create_other_location(station)
            general_staff = Staff.get_or_create_general_staff(station)
            staff_value = request.data['staff']
            if staff_value is None or staff_value == '':
                try:
                    location_staff = LocationStaff.objects.get(location=other_location, staff=general_staff, year_month=year_month)
                    location_staff.work_fraction = staff_value
                    location_staff.save()
                except ObjectDoesNotExist:
                    # LocationStaff does not exist and new values are blank - so ignore
                    pass
            else:
                try:
                    location_staff = LocationStaff.objects.get(location=other_location, staff=general_staff, year_month=year_month)
                except ObjectDoesNotExist:
                    location_staff = LocationStaff()
                    location_staff.location = other_location
                    location_staff.staff = general_staff
                    location_staff.year_month = year_month
                    
                location_staff.work_fraction = staff_value
                location_staff.save()
            
            arrests = request.data['arrests']
            if arrests is None or arrests == '':
                try:
                    location_statistics = LocationStatistics.objects.get(location=other_location, year_month=year_month)
                    location_statistics.arrests = arrests
                    location_statistics.save()
                except ObjectDoesNotExist:
                    # LocationStatistics does not exist and new valuse are blank - so ignore
                    pass
            else:
                try:
                    location_statistics = LocationStatistics.objects.get(location=other_location, year_month=year_month)
                except ObjectDoesNotExist:
                    location_statistics = LocationStatistics()
                    location_statistics.location = other_location
                    location_statistics.year_month = year_month
                
                location_statistics.arrests = arrests
                location_statistics.save()
                
        station_statistics.save()
        serializer = StationStatisticsSerializer(station_statistics, context={'request': request})
        return Response(serializer.data)
    
    def get_exchange_rate(self, request, country_id, year_month):
        try:
            exchange = CountryExchange.objects.get(country__id=country_id, year_month=year_month)
        except ObjectDoesNotExist:
            exchange = CountryExchange()
            exchange.country = Country.objects.get(id=country_id)
            exchange.year_month = year_month
            
            year = int(year_month) // 100
            month = int(year_month) % 100
            month -= 1
            if month < 1:
                month = 12
                year -= 1
            try:
                prior = CountryExchange.objects.get(country__id=country_id, year_month=(year * 100 + month))
                exchange.exchange_rate = prior.exchange_rate
            except:
                exchange.exchange_rate = 1
            exchange.save()
        serializer = CountryExchangeSerializer(exchange, context={'request': request})
        return Response(serializer.data)
    
    def update_exchange_rate(self, request):
        country_id = request.data['country']
        year_month = request.data['year_month']
        exchange_rate = request.data['exchange_rate']
        
        try:
            exchange = CountryExchange.objects.get(country__id=country_id, year_month=year_month)
        except:
            exchange = CountryExchange()
            exchange.country = Country.objects.get(id=country_id)
            exchange.year_month = year_month
        exchange.exchange_rate = exchange_rate
        exchange.save()
        serializer = CountryExchangeSerializer(exchange, context={'request': request})
        return Response(serializer.data)
    
    def set_country_data(self, request):
        with transaction.atomic():
            for entry in request.data:
                stationStatistics = StationStatistics.objects.get(id=entry['id'])
                for element in ['budget','gospel','empowerment','convictions']:
                    setattr(stationStatistics, element, entry[element])
                stationStatistics.save()
        return Response('')
    
    def sum_element(self, entry, name, value, default=None):
        if name not in entry:
            entry[name] = None
        if value is not None:
            if entry[name] is not None:
                entry[name] += value
            else:
                entry[name] = value
        
        if default is not None and (entry[name] is None or entry[name] == ''):
            entry[name] = default
    
    def apply_exchange_rate(self, value, country, year_month):
        try:
            exchange = CountryExchange.objects.get(country=country, year_month=year_month)
            rate = exchange.exchange_rate
        except:
            rate = 1.0
        
        if value is not None:
            value = int(value * 100 / rate)/100
        
        return value
    
    def countPopulated(self, entries, element):
        count = 0
        for entry in entries:
            if element in entry and entry[element] is not None and entry[element] != '':
                count += 1
        return count
    
    def retrieve_dashboard(self, request, country_id):
        current_date = datetime.datetime.now()
        month = current_date.month
        year = current_date.year
        if (current_date.day < 6):
            month -= 2
        else:
            month -= 1
        if month < 1:
            month = 12 + month
            year -= 1
        
        end_year_month = year * 100 + month
        end_date = str(year) + '-' + str(month) + '-01'
        if month < 6:
            start_year_month = (year - 1) * 100 + 12 + month - 5
            start_date = str(year - 1) + '-' + str(12 + month - 5) + '-01'
        else:
            start_year_month = year * 100 + month-5
            start_date = str(year) + '-' + str(month - 5) + '-01'
        country = Country.objects.get(id=country_id)
        dashboard={
            'month':datetime.date(year, month, 1).strftime('%B %Y'),
            'entries':[],
            'totals':{}}
        for non_transit in [False, True]:
            entries = StationStatistics.objects.filter(
                station__operating_country__id=country_id,
                station__non_transit=non_transit,
                year_month__gte=start_year_month,
                year_month__lte=end_year_month).order_by('station__station_name', '-year_month')
            
            dash_station = None
            for entry in entries:
                setattr(entry, 'intercepts', LocationStatistics.objects.filter(location__border_station=entry.station, year_month=entry.year_month).aggregate(Sum('intercepts'))['intercepts__sum'])
                setattr(entry, 'arrests', LocationStatistics.objects.filter(location__border_station=entry.station, year_month=entry.year_month).aggregate(Sum('arrests'))['arrests__sum'])
                if dash_station is None or dash_station['station_code'] != entry.station.station_code:
                    if dash_station is not None:
                        dashboard['entries'].append(dash_station)
                    dash_station = {
                        'station_name':entry.station.station_name,
                        'station_code':entry.station.station_code,
                        'station_open':entry.station.open,
                        'compliance':entry.compliance,
                        'last_budget':self.apply_exchange_rate(entry.budget, entry.station.operating_country, entry.year_month),
                        'last_intercepts':entry.intercepts,
                        'last_arrests':entry.arrests,
                        'last_gospel':entry.gospel,
                        'last_empowerment':entry.empowerment,
                        }
                    dash_station['to_date_intercepts'] = LocationStatistics.objects.filter(location__border_station=entry.station).aggregate(Sum('intercepts'))['intercepts__sum']
                    dash_station['to_date_arrests'] = LocationStatistics.objects.filter(location__border_station=entry.station).aggregate(Sum('arrests'))['arrests__sum']
                    dash_station['to_date_gospel'] = StationStatistics.objects.filter(station=entry.station).aggregate(Sum('gospel'))['gospel__sum']
                    dash_station['to_date_conv'] = StationStatistics.objects.filter(station=entry.station).aggregate(Sum('convictions'))['convictions__sum']
                    dash_station['to_date_irfs'] = IrfCommon.objects.filter(station=entry.station).count()
                    dash_station['to_date_cifs'] = CifCommon.objects.filter(station=entry.station).count()
                    dash_station['to_date_vdfs'] = VdfCommon.objects.filter(station=entry.station).count()
                    verdicts = LegalCaseSuspect.objects.filter(legal_case__station=entry.station, verdict_date__isnull=False, legal_case__charge_sheet_date__isnull=False)
                    dash_station['to_date_case_days'] = 0
                    dash_station['to_date_case_count'] = 0
                    for verdict in verdicts:
                        dash_station['to_date_case_days'] = (verdict.verdict_date - verdict.legal_case.charge_sheet_date).days
                        dash_station['to_date_case_count'] += 1
                        
                            
                    cifs = CifCommon.objects.filter(interview_date__gte=start_date,interview_date__lt=end_date,station=entry.station).count()
                    dash_station['6month_cifs'] = cifs
                    station_stats = StationStatistics.objects.filter(station=entry.station)
                    for station_stat in station_stats:
                        self.sum_element(dash_station, 'to_date_budget', self.apply_exchange_rate(station_stat.budget, station_stat.station.operating_country, station_stat.year_month))
                    try:
                        monthly = MonthlyReport.objects.get(station=entry.station, year=year, month=month)
                        dash_station['monthly_report'] = monthly.average_points
                    except ObjectDoesNotExist:
                        dash_station['monthly_report'] = None
                    
                    for element in ['last_budget', 'last_intercepts', 'last_arrests', 'last_gospel', 'last_empowerment',
                                    'to_date_intercepts', 'to_date_arrests', 'to_date_gospel','to_date_irfs', 'to_date_cifs',
                                    'to_date_vdfs', 'to_date_conv', 'to_date_case_days', 'to_date_case_count']:
                        if dash_station[element] is None or dash_station[element] == '':
                            dash_station[element] = 0
                    
                self.sum_element(dash_station, '6month_budget', self.apply_exchange_rate(entry.budget, entry.station.operating_country, entry.year_month), 0)
                for element in ['intercepts', 'arrests', 'gospel', 'empowerment']:
                    self.sum_element(dash_station, '6month_' + element, getattr(entry, element), 0)
        
            if dash_station is not None:
                dashboard['entries'].append(dash_station)
            
        for element in [
                    'monthly_report', 'compliance', '6month_budget', '6month_intercepts','6month_arrests','6month_gospel', '6month_empowerment', '6month_cifs',
                    'to_date_budget', 'to_date_intercepts', 'to_date_arrests', 'to_date_convictions', 'to_date_gospel','to_date_irfs', 'to_date_cifs',
                    'to_date_vdfs', 'to_date_conv', 'to_date_case_days', 'to_date_case_count',
                    'last_budget', 'last_intercepts',  'last_arrests', 'last_gospel', 'last_empowerment']:
            for entry in dashboard['entries']:
                self.sum_element(dashboard['totals'], element, entry.get(element, None), 0)
        
        if len(dashboard['totals']) > 0:
            dashboard['to_date'] = {
                    'intercepts': dashboard['totals']['to_date_intercepts'],
                    'arrests':dashboard['totals']['to_date_arrests']
                }
            self.sum_element(dashboard['to_date'], 'intercepts', country.prior_intercepts)
            self.sum_element(dashboard['to_date'], 'arrests', country.prior_arrests)
        
        for element in ['monthly_report', 'compliance']:
            if dashboard['totals'].get(element, None) is not None:
                populatedEntries = self.countPopulated(dashboard['entries'], element)
                if populatedEntries > 0:
                    dashboard['totals'][element] /= populatedEntries
        
        return Response (dashboard, status=status.HTTP_200_OK)
    
    def retrieve_location_staff(self, request, station_id, year_month):
        station = BorderStation.objects.get(id=station_id)
        Location.get_or_create_other_location(station)
        results = LocationStaff.objects.filter(location__border_station__id=station_id, year_month=year_month)
        serializer = LocationStaffSerializer(results, many=True, context={'request': request})
        return Response(serializer.data)

    def update_location_staff(self, request):
        location_id = request.data['location']
        staff_id = request.data['staff']
        year_month = request.data['year_month']
        try:
            location_staff = LocationStaff.objects.get(location__id=location_id, staff__id=staff_id, year_month=year_month)
        except ObjectDoesNotExist:
            location_staff = LocationStaff()
            location_staff.year_month = year_month
            location_staff.location = Location.objects.get(id=location_id)
            location_staff.staff = Staff.objects.get(id=staff_id)
        
        location_staff.work_fraction = request.data['work_fraction']
        location_staff.save()
        serializer = LocationStaffSerializer(location_staff, context={'request': request})
        return Response(serializer.data)
    
    def retrieve_location_statistics(self, request, station_id, year_month):
        station = BorderStation.objects.get(id=station_id)
        results = LocationStatistics.objects.filter(location__border_station__id=station_id, year_month=year_month)
        current_locations = []
        for result in results:
            current_locations.append(result.location)
        staff_entries = LocationStaff.objects.filter(location__border_station__id=station_id, year_month=year_month).exclude(location__in=current_locations)
        if len(staff_entries) > 0:
            for entry in staff_entries:
                location_statistics = LocationStatistics()
                location_statistics.location = entry.location
                location_statistics.year_month = entry.year_month
                location_statistics.save()
            results = LocationStatistics.objects.filter(location__border_station__id=station_id, year_month=year_month)
            
        serializer = LocationStatisticsSerializer(results, many=True, context={'request':request})
        return Response(serializer.data)
    
    def update_location_statistics(self, request):
        location_id = request.data['location']
        year_month = request.data['year_month']
        arrests = request.data['arrests']
        try:
            location_statistics = LocationStatistics.objects.get(location__id=location_id, year_month=year_month)
        except ObjectDoesNotExist:
            station = BorderStation.objects.get(id=station_id)
            if location_id is None:
                location = None
            else:
                location = Location.objects.get(id=location_id)
            location_statistics = LocationStatistics()
            location_statistics.location = location
            location_statistics.year_month = year_month
        
        location_statistics.arrests = arrests
        location_statistics.save()
        serializer = LocationStatisticsSerializer(location_statistics, context={'request': request})
        return Response(serializer.data)
        
        
            

