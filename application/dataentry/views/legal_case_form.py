import pytz
from templated_email import send_templated_mail

from rest_framework import serializers
from rest_framework import filters as fs
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.conf import settings

from dataentry.serialize_form import FormDataSerializer
from .base_form import BaseFormViewSet

from dataentry.form_data import Form, FormData
from dataentry.models import LegalCase, UserLocationPermission
from dataentry.serializers import LegalCaseSerializer
from dataentry.validate_form import ValidateForm

    
class LegalCaseFormViewSet(BaseFormViewSet):
    parser_classes = (MultiPartParser,FormParser,JSONParser)
    permission_classes = (IsAuthenticated, )
    serializer_class = LegalCaseSerializer
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ('legal_case_number', 'police_case', 'court_case')
    ordering_fields = ['legal_case_number', 'charge_sheet_date','case_type','date_last_contacted','missing_data_count' ]
    ordering = ('legal_case_number',)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return LegalCaseSerializer
        else:
            return FormDataSerializer
    
    def get_serializer_context(self): 
        return self.serializer_context

    def get_perm_group_name(self):
        return 'LEGAL_CASE'
    
    def get_form_type_name(self):
        return 'LEGAL_CASE'
    
    def get_element_paths(self):
        return [
            {
                'element':'scanned',
                'path':'legal_case_attachments/'
            }]
    
    def get_list_field_names(self):
        return ['id','legal_case_number']
        
    def get_empty_queryset(self):
        return LegalCase.objects.none()
    
    def filter_key(self, queryset, search):
        return queryset
    
    def send_verification_email(self, ulp, context):
        email_sender = settings.SERVER_EMAIL
        for user_location_permission in ulp:
            context['account'] = user_location_permission.account
            
            send_templated_mail(
                template_name='legal_case_submitted',
                from_email=email_sender,
                recipient_list=[user_location_permission.account.email],
                context=context
            )
    
    def pre_process(self, request, form_data):
        if form_data is not None:
            self.status = form_data.form_object.status
        else:
            self.status = None
    
    def post_process(self, request, form_data):
        validate = ValidateForm(form_data.form, form_data, False, mode="retrieve")
        validate.validate()
        form_data.form_object.missing_data_count = len(validate.warnings)
        form_data.form_object.save()
        
        if (self.status is None or self.status!='active') and form_data.form_object.status == 'active':
            context = {
                'legal_case__number': form_data.form_object.legal_case_number,
                'url': (settings.CLIENT_DOMAIN + '/legalCase/common:?id=' + str(form_data.form_object.id) +
                   '&stationId=' + str(form_data.form_object.station.id) +
                   '&countryId=' + str(form_data.form_object.station.operating_country.id) +
                   '&isViewing=false' + 
                   '&formName=' + form_data.form.form_name)
                }
            # Global permission to receive notification
            ulp1 = UserLocationPermission.objects.filter(permission__permission_group = 'NOTIFICATIONS', permission__action = 'LEGAL', station=None, country=None)
            
            # Country permission to receive notification
            ulp2 = UserLocationPermission.objects.filter(permission__permission_group = 'NOTIFICATIONS', permission__action = 'LEGAL', station=None, country=form_data.form_object.station.operating_country)
            
            ulp = (ulp1 | ulp2).distinct()
            self.send_verification_email(ulp, context)
            
    

