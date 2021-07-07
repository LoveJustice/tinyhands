import pytz

from rest_framework import serializers
from rest_framework import filters as fs
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.conf import settings
from templated_email import send_templated_mail

from dataentry.serialize_form import FormDataSerializer
from .base_form import BaseFormViewSet, BorderStationOverviewSerializer
from dataentry.serializers import GospelVerificationSerializer

from dataentry.form_data import Form, FormData
from dataentry.models import VdfCommon, GospelVerification, UserLocationPermission

class VdfListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    vdf_number = serializers.CharField()
    staff_name = serializers.CharField()
    date_of_interview = serializers.SerializerMethodField(read_only=True)
    date_time_entered_into_system = serializers.SerializerMethodField(read_only=True)
    date_time_last_updated = serializers.SerializerMethodField(read_only=True)
    station = BorderStationOverviewSerializer()
    form_name = serializers.SerializerMethodField(read_only=True)
    
    perm_group_name = 'VDF'
    
    def adjust_date_time_for_tz(self, date_time, tz_name):
        tz = pytz.timezone(tz_name)
        date_time = date_time.astimezone(tz)
        date_time = date_time.replace(microsecond=0)
        date_time = date_time.replace(tzinfo=None)
        return str(date_time)
    
    def get_date_of_interview(self, obj):
        if obj.interview_date is None:
            return ''
        else:
            return str(obj.interview_date.year) + '-' + str(obj.interview_date.month) + '-' + str(obj.interview_date.day)
    
    def get_date_time_entered_into_system(self, obj):
        tmp_date = self.adjust_date_time_for_tz (obj.date_time_entered_into_system, obj.station.time_zone)
        return tmp_date[0:10]
    
    def get_date_time_last_updated(self, obj):
        return self.adjust_date_time_for_tz (obj.date_time_last_updated, obj.station.time_zone)
    
    def get_form_name(self, obj):
        forms = Form.objects.filter(form_type__name='VDF', stations__id=obj.station.id)
        if len(forms) > 0:
            return forms[0].form_name
        else:
            return None
    
class VdfFormViewSet(BaseFormViewSet):
    parser_classes = (MultiPartParser,FormParser,JSONParser)
    permission_classes = (IsAuthenticated, )
    serializer_class = VdfListSerializer
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ('vdf_number',)
    ordering_fields = [
        'id', 'vdf_number', 'form_entered_by', 'staff_name', 
        'station', 'interview_date', 'date_time_entered_into_system',
        'date_time_last_updated']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return VdfListSerializer
        else:
            return FormDataSerializer
    
    def get_serializer_context(self): 
        return self.serializer_context
    
    def get_perm_group_name(self):
        return 'VDF'
    
    def get_form_type_name(self):
        return 'VDF'
    
    def get_element_paths(self):
        return [
            {
                'element':'scanned',
                'path':'vdf_attachments/'
            }]
    
    def get_list_field_names(self):
        return ['id', 'vdf_number', 'form_entered_by', 'staff_name', 
                'station', 'interview_date', 'date_time_entered_into_system',
                'date_time_last_updated']
        
    def get_empty_queryset(self):
        return VdfCommon.objects.none()
    
    def filter_key(self, queryset, search):
        return queryset.filter(vdf_number__contains=search)
    
    def pre_process(self, request, form_data):
        if form_data is not None:
            self.logbook_submitted = form_data.form_object.logbook_submitted
        else:
            self.logbook_submitted = None
    
    def send_home_situation_alert(self, ulp, context):
        email_sender = settings.SERVER_EMAIL
        for user_location_permission in ulp:
            send_templated_mail(
                template_name='home_situation_alert',
                from_email=email_sender,
                recipient_list=[user_location_permission.account.email],
                context=context
            )
    
    def post_process(self, request, form_data):
        vdf = form_data.form_object
        
        if self.logbook_submitted is not None or vdf.logbook_submitted is None:
            # Only process on the first submit
            return
        
        if vdf.victim_heard_message_before != 'Yes - heard and was believer' and vdf.what_victim_believes_now.startswith('Do believe'):
            existing_entry = GospelVerification.objects.filter(vdf=vdf)
            if len(existing_entry) < 1:
                gospel_verification = GospelVerification()
                gospel_verification.vdf = vdf
                gospel_verification.station = vdf.station
                gospel_verification.status = 'approved'
                gospel_verification.form_entered_by = vdf.form_entered_by
                gospel_verification.save()
        
        
        
        if vdf.total_situational_alarms < 10: 
            return
        
        victim_sent = vdf.where_victim_sent
        if vdf.where_victim_sent_details is not None and vdf.where_victim_sent_details != '':
            victim_sent += ':' + vdf.where_victim_sent_details
        
        context = {
            'vdf': vdf,
            'victim_sent': victim_sent,
            }
        
        # Global permission to receive notification
        ulp1 = UserLocationPermission.objects.filter(permission__permission_group = 'NOTIFICATIONS', permission__action = 'HSA', station=None, country=None)
        
        # Country permission to receive notification
        ulp2 = UserLocationPermission.objects.filter(permission__permission_group = 'NOTIFICATIONS', permission__action = 'HSA', station=None, country=form_data.form_object.station.operating_country)
        
        # station permission to receive notification
        ulp3 = UserLocationPermission.objects.filter(permission__permission_group = 'NOTIFICATIONS', permission__action = 'HSA', station=form_data.form_object.station)
        
        
        ulp = (ulp1 | ulp2 | ulp3).distinct()
        self.send_home_situation_alert(ulp, context)

class GospelVerificationViewSet(BaseFormViewSet):
    permission_classes = (IsAuthenticated, )
    serializer_class = GospelVerificationSerializer
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ('vdf__vdf_number','vdf__victim__full_name')
    ordering_fields = [
        'id', 'vdf__vdf_number', 'vdf__victim__full_name', 'vdf__interview_date', 
        'date_of_followup', 'profess_to_accept_christ']
    ordering = ('-vdf__interview_date',)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        filter = self.request.GET.get('filter')
        if  filter is not None:
            parts = filter.split(':')
            if len(parts) == 2:
                if parts[1] == 'True':
                    parts[1] = True
                elif parts[1] == 'False':
                    parts[1] = False
                queryset = queryset.filter(**{parts[0]:parts[1],})
        
        return queryset
    
    def filter_key(self, queryset, search):
        return queryset
    
    def get_perm_group_name(self):
        return 'GOSPEL_VERIFICATION'
    
    def get_form_type_name(self):
        return 'GOSPEL_VERIFICATION'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return GospelVerificationSerializer
        else:
            return FormDataSerializer
    
    def get_empty_queryset(self):
        return GospelVerification.objects.none()
    
    def get_list_field_names(self):
        return ['id', 'station', 'vdf', 'profess_to_accept_christ', 'survey_complete', 
                'searchlight_edited', 'date_of_followup', 'followup_person']
        
    def get_element_paths(self):
        return []

