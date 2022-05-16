import logging
import datetime
from decimal import Decimal

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
        results_qs = StationStatistics.objects.filter(station__operating_country__id=country_id, year_month=year_month).order_by('station__project_category__sort_order','station__station_name')
        
        serializer = StationStatisticsSerializer(results_qs , many=True, context={'request': request})
        return Response(serializer.data)
    
    def update_station_data(self, request):
        station_id = request.data['station']
        year_month = request.data['year_month']
        station = BorderStation.objects.get(id=station_id)
        if request.data['budget'] == '':
            budget = None
        else:
            budget = request.data['budget']
        if request.data['empowerment'] == '':
            empowerment = None
        else:
            empowerment = request.data['empowerment']
            
        try:
            station_statistics = StationStatistics.objects.get(station=station, year_month=year_month)
        except ObjectDoesNotExist:
            station_statistics = StationStatistics()
            station_statistics.station = station
            station_statistics.year_month = year_month
            
        station_statistics.budget = budget
        station_statistics.empowerment = empowerment
        if 'hasStaff' in station.features and (not station.operating_country.enable_all_locations or not 'hasLocationStaffing' in station.features):
            other_location = Location.get_or_create_other_location(station)
            general_staff = Staff.get_or_create_general_staff(station)
            if request.data['staff'] == '':
                staff_value = None
            else:
                staff_value = request.data['staff']
            if staff_value is None:
                try:
                    location_staff = LocationStaff.objects.get(location=other_location, staff=general_staff, year_month=year_month)
                    location_staff.work_fraction = None
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
            
        if not station.operating_country.enable_all_locations:
            # if enable_all_lcoations is not true, then the arrests can be updated here
            arrests = request.data['arrests']
            if arrests is None or arrests=="":
                try:
                    location_statistics = LocationStatistics.objects.get(location=other_location, year_month=year_month)
                    location_statistics.arrests = None
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
            rate = Decimal(exchange.exchange_rate)
        except:
            rate = 1.0
        
        if value is not None:
            value = int(value * 100 / Decimal(rate))/100
        
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
        
        month -= 1
        if month < 1:
            month = 12 + month
            year -= 1
        
        start_staff = str(year) + '-' + str(month) + '-01'
        if month == 12:
            end_staff = str(year+1) + '-01-01'
        else:
            end_staff = str(year) + '-' + str(month+1) + '-01'
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
            'categories':[],
            'entries':[],
            'totals':{}}
                
        entries = StationStatistics.objects.filter(
            station__operating_country__id=country_id,
            station__features__contains='hasProjectStats',
            year_month__gte=start_year_month,
            year_month__lte=end_year_month).order_by('station__project_category__sort_order','station__station_name', '-year_month')
        
        dash_station = None
        print('here')
        categories = []
        for entry in entries:
            setattr(entry, 'intercepts', LocationStatistics.objects.filter(location__border_station=entry.station, year_month=entry.year_month).aggregate(Sum('intercepts'))['intercepts__sum'])
            setattr(entry, 'arrests', LocationStatistics.objects.filter(location__border_station=entry.station, year_month=entry.year_month).aggregate(Sum('arrests'))['arrests__sum'])
            if entry.station.project_category.name not in categories:
                if dash_station is not None:
                    category['entries'].append(dash_station)
                    dash_station = None
                categories.append(entry.station.project_category.name)
                print('category name', entry.station.project_category.name, 'code', entry.station.station_code)
                category ={
                    'name': entry.station.project_category.name,
                    'entries': [],
                    'subtotals': {}
                    }
                dashboard['categories'].append(category)
                
            if dash_station is None or dash_station['station_code'] != entry.station.station_code:
                if dash_station is not None:
                    category['entries'].append(dash_station)
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
                    'last_staff_count': LocationStaff.objects.filter(location__border_station=entry.station, year_month=end_year_month).aggregate(Sum('work_fraction'))['work_fraction__sum'],
                    'last_subcommittee_count':entry.subcommittee_members
                    }
                dash_station['to_date_intercepts'] = LocationStatistics.objects.filter(location__border_station=entry.station).aggregate(Sum('intercepts'))['intercepts__sum']
                dash_station['to_date_arrests'] = LocationStatistics.objects.filter(location__border_station=entry.station).aggregate(Sum('arrests'))['arrests__sum']
                dash_station['to_date_gospel'] = StationStatistics.objects.filter(station=entry.station).aggregate(Sum('gospel'))['gospel__sum']
                dash_station['to_date_conv'] = StationStatistics.objects.filter(station=entry.station).aggregate(Sum('convictions'))['convictions__sum']
                dash_station['to_date_irfs'] = IrfCommon.objects.filter(station=entry.station).count()
                dash_station['to_date_cifs'] = CifCommon.objects.filter(station=entry.station).count()
                dash_station['to_date_vdfs'] = VdfCommon.objects.filter(station=entry.station).count()
                dash_station['to_date_emp'] = StationStatistics.objects.filter(station=entry.station).aggregate(Sum('empowerment'))['empowerment__sum']
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
                                'to_date_vdfs', 'to_date_emp', 'to_date_conv', 'to_date_case_days', 'to_date_case_count']:
                    if dash_station[element] is None or dash_station[element] == '':
                        dash_station[element] = 0
                    
            self.sum_element(dash_station, '6month_budget', self.apply_exchange_rate(entry.budget, entry.station.operating_country, entry.year_month), 0)
            for element in ['intercepts', 'arrests', 'gospel', 'empowerment']:
                self.sum_element(dash_station, '6month_' + element, getattr(entry, element), 0)
        
        if dash_station is not None:
            category['entries'].append(dash_station)
            
        for element in [
                    'monthly_report', 'compliance', '6month_budget', '6month_intercepts','6month_arrests','6month_gospel', '6month_empowerment', '6month_cifs',
                    'to_date_budget', 'to_date_intercepts', 'to_date_arrests', 'to_date_convictions', 'to_date_gospel','to_date_irfs', 'to_date_cifs',
                    'to_date_vdfs', 'to_date_emp', 'to_date_conv', 'to_date_case_days', 'to_date_case_count',
                    'last_budget', 'last_intercepts',  'last_arrests', 'last_gospel', 'last_empowerment','last_staff_count','last_subcommittee_count']:
            for category in dashboard['categories']:
                for entry in category['entries']:
                    self.sum_element(category['subtotals'], element, entry.get(element, None), 0)
                self.sum_element(dashboard['totals'], element, category['subtotals'].get(element, None), 0)
        
        if len(dashboard['totals']) > 0:
            dashboard['to_date'] = {
                    'intercepts': dashboard['totals']['to_date_intercepts'],
                    'arrests':dashboard['totals']['to_date_arrests']
                }
            self.sum_element(dashboard['to_date'], 'intercepts', country.prior_intercepts)
            self.sum_element(dashboard['to_date'], 'arrests', country.prior_arrests)
        
        for element in ['monthly_report', 'compliance']:
            total_populated = 0
            for category in dashboard['categories']:
                if category['subtotals'].get(element, None) is not None:
                    populatedEntries = self.countPopulated(category['entries'], element)
                    total_populated += populatedEntries
                    if populatedEntries > 0:
                        category['subtotals'][element] /= populatedEntries
            if dashboard['totals'].get(element, None) is not None and total_populated > 0:
                dashboard['totals'][element] /= total_populated
        
        return Response (dashboard, status=status.HTTP_200_OK)
    
    """
        Need custom method to retrieve staff for a location for a particular year month.  This needs to return all
        staff currently assigned to work at the station.  It also needs to include any staff who were assigned to work
        at the station in that year and month, but are not currently assigned.
    """
    def retrieve_location_staff_staff(self, request, station_id, year_month):
        staff = []
        # Get any staff that already has stats for the project for the year/month
        stats_for_month_list = LocationStatistics.object.filter(location__border_station__id=station_id, year_month=year_month)
        for stats in stats_for_month_list:
            if stats.staff not in staff:
                staff.append(stats.staff)
        # Get active staff currently assigned on the project
        works_on_list = WorksOnProject.objects.filter(border_station__id=station_id)
        for works_on in works_on_list:
            if works_on.staff not in staff and works_on.staff.last_date is None:
                staff.append(works_on.staff)
        
        serializer = self.get_serializer(staff, many=True)
        return Response(serializer.data)
    
    def retrieve_location_staff(self, request, station_id, year_month):
        station = BorderStation.objects.get(id=station_id)
        results = LocationStaff.objects.filter(location__border_station__id=station_id, year_month=year_month)
        serializer = LocationStaffSerializer(results, many=True, context={'request': request})
        return Response(serializer.data)

    def update_location_staff(self, request):
        location_id = request.data['location']
        staff_id = request.data['staff']
        year_month = request.data['year_month']
        location = Location.objects.get(id=location_id)
        try:
            station_statistics = StationStatistics.objects.get(station=location.border_station, year_month=year_month)
        except ObjectDoesNotExist:
            station_statistics = StationStatistics()
            station_statistics.station = location.border_station
            station_statistics.year_month = year_month
            station_statistics.save()
        
        try:
            location_staff = LocationStaff.objects.get(location__id=location_id, staff__id=staff_id, year_month=year_month)
        except ObjectDoesNotExist:
            location_staff = LocationStaff()
            location_staff.year_month = year_month
            location_staff.location = Location.objects.get(id=location_id)
            location_staff.staff = Staff.objects.get(id=staff_id)
        
        if request.data['work_fraction'] == '':
            work_fraction = None
        else:
            work_fraction = request.data['work_fraction']
        location_staff.work_fraction = work_fraction
        location_staff.save()
        serializer = LocationStaffSerializer(location_staff, context={'request': request})
        return Response(serializer.data)
    
    def retrieve_location_statistics(self, request, station_id, year_month):
        station = BorderStation.objects.get(id=station_id)
        results = LocationStatistics.objects.filter(location__border_station__id=station_id, year_month=year_month)
        current_locations = []
        for result in results:
            current_locations.append(result.location)
        staff_entries = LocationStaff.objects.filter(location__border_station__id=station_id, year_month=year_month).exclude(location__in=current_locations).order_by('location')
        if len(staff_entries) > 0:
            last_location = None
            for entry in staff_entries:
                if entry.location != last_location:
                    last_location = entry.location
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
        location = Location.objects.get(id=location_id)
        try:
            station_statistics = StationStatistics.objects.get(station=location.border_station, year_month=year_month)
        except ObjectDoesNotExist:
            station_statistics = StationStatistics()
            station_statistics.station = location.border_station
            station_statistics.year_month = year_month
            station_statistics.save()
            
        if request.data['arrests'] == '':
            arrests = None
        else:
            arrests = request.data['arrests']
        try:
            location_statistics = LocationStatistics.objects.get(location__id=location_id, year_month=year_month)
        except ObjectDoesNotExist:
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
        
        
            

