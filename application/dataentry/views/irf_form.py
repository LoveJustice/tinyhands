import pytz
from datetime import timedelta

from django.utils import timezone
from django.db.models import Q

from rest_framework import status
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import filters as fs
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from dataentry.serialize_form import FormDataSerializer
from .base_form import BaseFormViewSet, BorderStationOverviewSerializer

from dataentry.form_data import Form, FormData
from dataentry.models import IrfNepal, UserLocationPermission

class IrfListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    status = serializers.SerializerMethodField(read_only=True)
    irf_number = serializers.CharField()
    number_of_victims = serializers.IntegerField()
    number_of_traffickers = serializers.IntegerField()
    staff_name = serializers.CharField()
    date_time_of_interception = serializers.SerializerMethodField(read_only=True)
    date_time_entered_into_system = serializers.SerializerMethodField(read_only=True)
    date_time_last_updated = serializers.SerializerMethodField(read_only=True)
    station = BorderStationOverviewSerializer()
    form_name = serializers.SerializerMethodField(read_only=True)
    can_view = serializers.SerializerMethodField(read_only=True)
    can_edit = serializers.SerializerMethodField(read_only=True)
    can_delete = serializers.SerializerMethodField(read_only=True)
    can_approve = serializers.SerializerMethodField(read_only=True)
    
    perm_group_name = 'IRF'
    
    def get_evidence_code(self, value):
        code = ''
        if value is None:
            code = ''
        elif value.startswith('Clear Evidence'):
            code = 'CE'
        elif value.startswith('Some Evidence'):
            code = 'SE'
        elif value.startswith('High Risk'):
            code='HR'
        elif value.startswith('Should Not have Intercepted'):
            code = 'SNHI'
        
        return code
    
    def get_status(self, obj):
        if obj.status == 'approved':
            status = 'A-' + self.get_evidence_code(obj.evidence_categorization)
        elif obj.status == 'first-verification':
            status = '1V-' + self.get_evidence_code(obj.logbook_first_verification)
        elif obj.status == 'second-verification':
            status = '2V-' + self.get_evidence_code(obj.logbook_second_verification)
        elif obj.status == 'invalid':
            status = '2V-SNHI'
        else:
            status = obj.status
            
        return status
    
    def adjust_date_time_for_tz(self, date_time, tz_name):
        tz = pytz.timezone(tz_name)
        date_time = date_time.astimezone(tz)
        date_time = date_time.replace(microsecond=0)
        date_time = date_time.replace(tzinfo=None)
        return str(date_time)
    
    def get_date_time_of_interception(self, obj):
        return self.adjust_date_time_for_tz (obj.date_time_of_interception, obj.station.time_zone)
    
    def get_date_time_entered_into_system(self, obj):
        return self.adjust_date_time_for_tz (obj.date_time_entered_into_system, obj.station.time_zone)
    
    def get_date_time_last_updated(self, obj):
        return self.adjust_date_time_for_tz (obj.date_time_last_updated, obj.station.time_zone)
    
    def get_form_name(self, obj):
        forms = Form.objects.filter(form_type__name='IRF', stations__id=obj.station.id)
        if len(forms) > 0:
            return forms[0].form_name
        else:
            return None
    
    def get_can_view(self, obj):
        perm_list = self.context.get('perm_list')
        return UserLocationPermission.has_permission_in_list(perm_list, self.perm_group_name,'VIEW', obj.station.operating_country.id, obj.station.id)
    
    def get_can_edit(self, obj):
        perm_list = self.context.get('perm_list')
        ret =  UserLocationPermission.has_permission_in_list(perm_list, self.perm_group_name,'EDIT', obj.station.operating_country.id, obj.station.id)
        return ret
    
    def get_can_delete(self, obj):
        perm_list = self.context.get('perm_list')
        return UserLocationPermission.has_permission_in_list(perm_list, self.perm_group_name,'DELETE', obj.station.operating_country.id, obj.station.id)
    
    def get_can_approve(self, obj):
        perm_list = self.context.get('perm_list')
        return UserLocationPermission.has_permission_in_list(perm_list, self.perm_group_name,'APPROVE', obj.station.operating_country.id, obj.station.id)

class IrfFormViewSet(BaseFormViewSet):
    parser_classes = (MultiPartParser,FormParser,JSONParser)
    permission_classes = (IsAuthenticated, )
    serializer_class = IrfListSerializer
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ('irf_number',)
    ordering_fields = (
        'irf_number', 'staff_name', 'number_of_victims', 'number_of_traffickers', 'date_time_of_interception',
        'date_time_entered_into_system', 'date_time_last_updated',)
    ordering = ('-date_time_of_interception',)
    
    def or_filter(self, current_qfilter, new_qfilter):
        if current_qfilter is None:
            return new_qfilter
        else:
            return current_qfilter | new_qfilter
        
    def build_query_filter(self, status_list, station_list, in_progress, account_id):
        status_map = {
            'A': 'approved',
            '1V': 'first-verification',
            '2V': 'second-verification'
            }
        status_evidence_field_map = {
            'A': 'evidence_categorization',
            '1V': 'logbook_first_verification',
            '2V': 'logbook_second_verification'
            }
        evidence_map = {
            'CE': 'Clear Evidence',
            'SE': 'Some Evidence',
            'HR': 'High Risk',
            'SNHI': 'Should Not have Intercepted',
            }
        if in_progress:
            q_filter = Q(status='in-progress')&Q(form_entered_by__id=account_id)
        else:
            q_filter = Q()
        
        all_evidence = {}
        
        if 'A-CE' in status_list and 'A-SE' in status_list and 'A-HR' in status_list:
            all_evidence['A'] = True
            q_filter = q_filter | Q(status='approved')
       
        if '1V-CE' in status_list and '1V-SE' in status_list and '1V-HR' in status_list and '1V-SNHI' in status_list:
            all_evidence['1V'] = True
            q_filter = q_filter | Q(status=status_map['1V'])
            
        if '2V-CE' in status_list and '2V-SE' in status_list and '2V-HR' in status_list:
            all_evidence['2V'] = True
            q_filter = q_filter | Q(status=status_map['2V'])
            if '2V-SNHI' in status_list:
                q_filter = q_filter | Q(status='invalid')
        
        for status in status_list:
            parts = status.split('-')
            if len(parts) < 2:
                continue
            
            if parts[0] in all_evidence and all_evidence[parts[0]]:
                continue
            
            if parts[1] in evidence_map:
                evidence = evidence_map[parts[1]]
            else:
                continue
            
            evidence_match = (status_evidence_field_map[parts[0]] + '__startswith', evidence)
            
            if parts[0] == '2V' and parts[1] == 'SNHI':
                q_filter = q_filter | Q(status='invalid')
            else:
                q_filter = q_filter | Q(status=status_map[parts[0]])&Q(evidence_match)
        
        if q_filter is not None and len(station_list) > 0:
            q_filter = q_filter & Q(station__in=station_list)
            
        return q_filter
    
    def get_serializer_class(self):
        if self.action == 'list':
            return IrfListSerializer
        else:
            return FormDataSerializer
    
    def get_serializer_context(self): 
        return self.serializer_context
    
    def get_perm_group_name(self):
        return 'IRF'
    
    def get_form_type_name(self):
        return 'IRF'
    
    def get_element_paths(self):
        return [
            {
                'element':'images',
                'path':'interceptee_photos/'
            },
            {
                'element':'scanned',
                'path':'scanned_irf_forms/'
            }
        ]
    
    def get_list_field_names(self):
        return ['id', 'irf_number', 'form_entered_by', 'number_of_victims', 'number_of_traffickers', 'staff_name', 
                    'station', 'date_time_of_interception', 'date_time_entered_into_system',
                    'date_time_last_updated', 'status', 'evidence_categorization', 'logbook_first_verification',
                    'logbook_second_verification']
        
    def get_empty_queryset(self):
        return IrfNepal.objects.none()
    
    def filter_key(self, queryset, search):
        return queryset.filter(irf_number__contains=search)
    
    def tally(self, request):
        results = {'id': request.user.id}
        self.action = 'list'
        queryset = self.get_queryset();
        today = timezone.now().now()
        dates = [today - timedelta(days=x) for x in range(7)]
        day_records_list = []
        for date in dates:
            day_records = {'date': date, 'interceptions': {}}
            interceptions = day_records['interceptions']
            records = queryset.filter(date_time_entered_into_system__year=date.year, date_time_entered_into_system__month=date.month, date_time_entered_into_system__day=date.day)
            for record in records:
                station_code = record.irf_number[:3]
                victims = record.interceptees.filter(kind='v')
                count = len(victims)
                if station_code not in list(interceptions.keys()):
                    interceptions[station_code] = 0
                interceptions[station_code] += count
            
            day_records_list.append(day_records)
            
        results['days'] = day_records_list
        ytd_records = queryset.filter(date_time_entered_into_system__year=today.year)
        ytd_count = 0
        for record in ytd_records:
            victims = record.interceptees.filter(kind='v')
            ytd_count += len(victims)
        results['ytd'] = ytd_count
        
        return Response(results, status=status.HTTP_200_OK)
        


