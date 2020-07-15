import logging
import datetime

from rest_framework import filters as fs
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.db import transaction
from dataentry.models import OperationsData
from dataentry.serializers import OperationsDataSerializer
from rest_api.authentication import HasPostPermission, HasPutPermission, HasDeletePermission

from dataentry.models import Country, OperationsData, MonthlyReport

logger = logging.getLogger(__name__)

class OperationsDataViewSet(viewsets.ModelViewSet):
    queryset = OperationsData.objects.all()
    serializer_class = OperationsDataSerializer
    permission_classes = (IsAuthenticated, )
    
    def retrieve_country_data(self, request, country_id, year_month):
        results = OperationsData.objects.filter(station__operating_country__id=country_id, year_month=year_month).order_by('station__non_transit', 'station__station_name')
        
        serializer = OperationsDataSerializer(results , many=True, context={'request': request})
        return Response(serializer.data)
    
    def set_country_data(self, request):
        with transaction.atomic():
            for entry in request.data:
                operationsData = OperationsData.objects.get(id=entry['id'])
                for element in ['budget','intercepts','arrests','gospel','empowerment','convictions']:
                    setattr(operationsData, element, entry[element])
                operationsData.save()
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
    
    def apply_exchange_rate(self, value, rate):
        if value is not None:
            value = int (value / rate)
        
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
        if month < 6:
            start_year_month = (year - 1) * 100 + 12 + month - 5
        else:
            start_year_month = year * 100 + month-5
        country = Country.objects.get(id=country_id)
        dashboard={
            'month':datetime.date(year, month, 1).strftime('%B %Y'),
            'entries':[],
            'totals':{}}
        for non_transit in [False, True]:
            entries = OperationsData.objects.filter(
                station__operating_country__id=country_id,
                station__non_transit=non_transit,
                year_month__gte=start_year_month,
                year_month__lte=end_year_month).order_by('station__station_name', '-year_month')
            
            dash_station = None
            for entry in entries:
                if dash_station is None or dash_station['station_code'] != entry.station.station_code:
                    if dash_station is not None:
                        dashboard['entries'].append(dash_station)
                    dash_station = {
                        'station_name':entry.station.station_name,
                        'station_code':entry.station.station_code,
                        'station_open':entry.station.open,
                        'compliance':entry.compliance,
                        'last_budget':self.apply_exchange_rate(entry.budget, country.exchange_rate),
                        'last_intercepts':entry.intercepts,
                        'last_arrests':entry.arrests,
                        'last_gospel':entry.gospel,
                        'last_empowerment':entry.empowerment,
                        'last_cifs':entry.cifs,
                        }
                    dash_station['to_date_intercepts'] = OperationsData.objects.filter(station=entry.station).aggregate(Sum('intercepts'))['intercepts__sum']
                    dash_station['to_date_arrests'] = OperationsData.objects.filter(station=entry.station).aggregate(Sum('arrests'))['arrests__sum']
                    dash_station['to_date_convictions'] = OperationsData.objects.filter(station=entry.station).aggregate(Sum('convictions'))['convictions__sum']
                    try:
                        monthly = MonthlyReport.objects.get(station=entry.station, year=year, month=month)
                        dash_station['monthly_report'] = monthly.average_points
                    except ObjectDoesNotExist:
                        dash_station['monthly_report'] = None
                    
                    for element in ['last_budget', 'last_intercepts', 'last_arrests', 'last_gospel', 'last_empowerment', 'last_cifs',
                                    'to_date_intercepts', 'to_date_arrests', 'to_date_convictions']:
                        if dash_station[element] is None or dash_station[element] == '':
                            dash_station[element] = 0
            
                self.sum_element(dash_station, '6month_budget', self.apply_exchange_rate(entry.budget, country.exchange_rate), 0)
                for element in ['intercepts', 'arrests', 'gospel', 'empowerment', 'cifs']:
                    self.sum_element(dash_station, '6month_' + element, getattr(entry, element), 0)
        
            if dash_station is not None:
                dashboard['entries'].append(dash_station)
            
        for element in [
                    'monthly_report', 'compliance', '6month_budget', '6month_intercepts','6month_arrests','6month_gospel', '6month_empowerment', '6month_cifs',
                    'to_date_intercepts', 'to_date_arrests', 'to_date_convictions',
                    'last_budget', 'last_intercepts',  'last_arrests', 'last_gospel', 'last_empowerment']:
            for entry in dashboard['entries']:
                self.sum_element(dashboard['totals'], element, entry.get(element, None), 0)
        
        for element in ['monthly_report', 'compliance']:
            if dashboard['totals'].get(element, None) is not None:
                populatedEntries = self.countPopulated(dashboard['entries'], element)
                if populatedEntries > 0:
                    dashboard['totals'][element] /= populatedEntries
        
        return Response (dashboard, status=status.HTTP_200_OK)

