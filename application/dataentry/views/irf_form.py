import pytz
import datetime
from datetime import timedelta
import traceback

from django.utils import timezone
from django.db.models import Q
from django.conf import settings
from templated_email import send_templated_mail

from rest_framework import status
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import filters as fs
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from dataentry.serialize_form import FormDataSerializer
from .base_form import BaseFormViewSet, BorderStationOverviewSerializer

from dataentry.form_data import Form, FormData
from dataentry.models import IntercepteeCommon, InterceptionCache, IrfCommon, IrfVerification, UserLocationPermission

class IrfListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    status = serializers.SerializerMethodField(read_only=True)
    irf_number = serializers.CharField()
    number_of_victims = serializers.IntegerField()
    number_of_traffickers = serializers.IntegerField()
    staff_name = serializers.CharField()
    date_time_of_interception = serializers.SerializerMethodField(read_only=True)
    date_time_last_updated = serializers.SerializerMethodField(read_only=True)
    station = BorderStationOverviewSerializer()
    form_name = serializers.SerializerMethodField(read_only=True)
    logbook_first_verification_date = serializers.DateField()
    verified_date = serializers.DateField()
    can_view = serializers.SerializerMethodField(read_only=True)
    can_edit = serializers.SerializerMethodField(read_only=True)
    can_delete = serializers.SerializerMethodField(read_only=True)
    can_approve = serializers.SerializerMethodField(read_only=True)
    
    perm_group_name = 'IRF'
    
    def get_status(self, obj):
        if obj.status == 'approved':
            if obj.evidence_categorization is None or obj.evidence_categorization == '':
                status = 'old'
            else:
                status = 'submitted'
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
        date_time_of_interception = str(obj.date_of_interception)
        if obj.time_of_interception is not None:
            date_time_of_interception += ' ' + str(obj.time_of_interception)
        return date_time_of_interception
    
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
        'irf_number', 'staff_name', 'number_of_victims', 'number_of_traffickers', 'date_of_interception', 'time_of_interception',
        'date_time_last_updated', 'verified_date',)
    ordering = ('-date_of_interception', '-time_of_interception')
    
    def or_filter(self, current_qfilter, new_qfilter):
        if current_qfilter is None:
            return new_qfilter
        else:
            return current_qfilter | new_qfilter
        
    def build_query_filter(self, status_list, in_station_list, in_progress, account_id):
        can_verify = self.request.GET.get('may_verify', None)
        exclude_account_verified_irfs = []
        if can_verify == 'true':
            perm_list = UserLocationPermission.objects.filter(account__id=account_id,
                                                              permission__permission_group=self.get_perm_group_name(),
                                                              permission__action='EDIT')
            station_list = []
            for station in in_station_list:
                if (UserLocationPermission.has_permission_in_list(perm_list, self.get_perm_group_name(), 'EDIT', station.operating_country.id, station.id)):
                    station_list.append(station)
            exclude_account_verified_irfs = IrfVerification.objects.filter(verifier__id = account_id).values_list('interception_record__id', flat = True)
        else:
            station_list = in_station_list
                    
        if len(status_list) < 1:
            if in_progress:
                return Q(status='in-progress')&Q(form_entered_by__id=account_id)&Q(station__in=station_list)
            else:
                return Q(station__in=station_list)
        
        if status_list[0] == '!invalid':
            q_filter = Q(status='in-progress')&Q(form_entered_by__id=account_id)|~Q(status='in-progress')&~Q(status='invalid')&Q(station__in=station_list)
        else:
            q_filter = None
            filter_parts = status_list[0].split('|')
            for filter_part in filter_parts:
                if q_filter is None:
                    q_filter = Q(status=filter_part)
                else:
                    q_filter = q_filter | Q(status=filter_part)
            q_filter = (q_filter)&Q(station__in=station_list)
        
        if can_verify == 'true':
            q_filter = q_filter & ~Q(id__in=exclude_account_verified_irfs)
        
        if len(status_list) > 1:
            if status_list[1] == '!None':
                q_filter = q_filter & Q(evidence_categorization__isnull=False) & ~Q(evidence_categorization='')
            elif status_list[1] == 'None':
                q_filter = q_filter & (Q(evidence_categorization__isnull=True) | Q(evidence_categorization=''))
            else:
                q_filter = q_filter & Q(verified_evidence_categorization__startswith=status_list[1])
        
        date_filter = self.request.GET.get('date_filter', None)
        if date_filter is not None and date_filter != 'None':
            date_start = self.request.GET.get('date_start', None)
            date_end = self.request.GET.get('date_end', None)
            if date_filter == 'First Verification':
                q_filter = q_filter & Q(logbook_first_verification_date__gte=date_start) & Q(logbook_first_verification_date__lte=date_end)
            elif date_filter == 'Second Verification':
                q_filter = q_filter & Q(verified_date__gte=date_start) & Q(verified_date__lte=date_end)
            elif date_filter == 'Interception':
                q_filter = q_filter & Q(date_of_interception__gte=date_start) & Q(date_of_interception__lte=date_end)
                
        
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
                    'station', 'date_of_interception', 'time_of_interception', 'date_time_last_updated', 'status', 'evidence_categorization', 'logbook_first_verification',
                    'logbook_first_verification_date', 'verified_evidence_categorization', 'verified_date']
        
    def get_empty_queryset(self):
        return IrfCommon.objects.none()
    
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
                victims = record.interceptees.filter(person__role='PVOT')
                count = len(victims)
                if station_code not in list(interceptions.keys()):
                    interceptions[station_code] = 0
                interceptions[station_code] += count
            
            day_records_list.append(day_records)
            
        results['days'] = day_records_list
        ytd_records = queryset.filter(date_time_entered_into_system__year=today.year)
        ytd_count = 0
        for record in ytd_records:
            victims = record.interceptees.filter(person__role='PVOT')
            ytd_count += len(victims)
        results['ytd'] = ytd_count
        
        return Response(results, status=status.HTTP_200_OK)
     
    
    @staticmethod
    def get_six_month_tally():
        today = timezone.now().now()
        try:
            cache = InterceptionCache.objects.get(reference_date=today)
        except:
            start_date = today - timedelta(days=180)
            interceptions = IntercepteeCommon.objects.filter(person__role='PVOT',
                                                interception_record__verified_date__gte=start_date,
                                                interception_record__verified_date__lte=today).order_by(
                                                    'interception_record__station__operating_country__region__name',
                                                    'interception_record__station__operating_country__name'
                                                    )
            results= {'count':0, 'regions':[]}                                    
            region_results = {'name':'', 'count':0, 'countries':[]}
            country_results = {'name':'', 'count':0}
            for interception in interceptions:
                if interception.interception_record.station.operating_country.name != country_results['name']:
                    if country_results['count'] > 0:
                        region_results['countries'].append(country_results)
                        region_results['count'] += country_results['count']
                    country_results = {'name':interception.interception_record.station.operating_country.name, 'count':1}
                else:
                    country_results['count'] += 1
                if interception.interception_record.station.operating_country.region.name != region_results['name']:
                    if region_results['count'] > 0:
                        results['regions'].append(region_results)
                        results['count'] += region_results['count']
                    region_results = {'name':interception.interception_record.station.operating_country.region.name, 'count':0, 'countries':[]}
            if country_results['count'] > 0:
                region_results['countries'].append(country_results)
                region_results['count'] += country_results['count']
                results['regions'].append(region_results)
                results['count'] += region_results['count']
        
                cache = InterceptionCache()
                cache.reference_date = today
            cache.interceptions = results
            cache.save()
        
        return cache.interceptions
    
    def six_month_tally(self, request):        
        return Response(IrfFormViewSet.get_six_month_tally(), status=status.HTTP_200_OK)

    def pre_process(self, request, form_data):
        if form_data is not None:
            self.logbook_submitted = form_data.form_object.logbook_submitted
            self.logbook_first_verification_date = form_data.form_object.logbook_first_verification_date
        else:
            self.logbook_submitted = None
            self.logbook_first_verification_date = None
    
    def send_verification_email(self, ulp, context):
        email_sender = settings.SERVER_EMAIL
        for user_location_permission in ulp:
            context['account'] = user_location_permission.account
            
            send_templated_mail(
                template_name='verification_notice',
                from_email=email_sender,
                recipient_list=[user_location_permission.account.email],
                context=context
            )
    
    def post_process(self, request, form_data):
        try:
            start_check = datetime.datetime(2020,4,1, tzinfo=datetime.timezone.utc)
            if form_data.form_object.verified_date is not None or form_data.form_object.date_of_interception < start_check.date():
                return
            context = {
                'irf_number': form_data.form_object.irf_number,
                'url': (settings.CLIENT_DOMAIN + '/irf/' + form_data.form.form_name[3:].lower() + ':?id=' + str(form_data.form_object.id) +
                   '&stationId=' + str(form_data.form_object.station.id) +
                   '&countryId=' + str(form_data.form_object.station.operating_country.id) +
                   '&isViewing=false' + 
                   '&formName=' + form_data.form.form_name)
                }
            if self.logbook_first_verification_date is None and form_data.form_object.logbook_first_verification_date is not None:
                context['event'] = 'verified'
                context['stage'] = 'second'
                action='IRF_VERIFIED'
            elif self.logbook_submitted is None and form_data.form_object.logbook_submitted is not None and form_data.form_object.logbook_first_verification_date is None:
                context['event'] = 'entered'
                context['stage'] = 'first'
                action='IRF_SUBMITTED'
            else:
                return
            
            # Global permission to receive notification
            ulp1 = UserLocationPermission.objects.filter(permission__permission_group = 'NOTIFICATIONS', permission__action = action, station=None, country=None)
            
            # Country permission to receive notification
            ulp2 = UserLocationPermission.objects.filter(permission__permission_group = 'NOTIFICATIONS', permission__action = action, station=None, country=form_data.form_object.station.operating_country)
            
            # station permission to receive notification
            ulp3 = UserLocationPermission.objects.filter(permission__permission_group = 'NOTIFICATIONS', permission__action = action, station=form_data.form_object.station)
            
            ulp = (ulp1 | ulp2 | ulp3).distinct()
            self.send_verification_email(ulp, context)
        except:
            print (traceback.format_exc())

