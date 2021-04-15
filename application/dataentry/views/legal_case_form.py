import pytz

from rest_framework import serializers
from rest_framework import filters as fs
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from dataentry.serialize_form import FormDataSerializer
from .base_form import BaseFormViewSet

from dataentry.form_data import Form, FormData
from dataentry.models import LegalCase
from dataentry.serializers import LegalCaseSerializer
from dataentry.validate_form import ValidateForm

    
class LegalCaseFormViewSet(BaseFormViewSet):
    parser_classes = (MultiPartParser,FormParser,JSONParser)
    permission_classes = (IsAuthenticated, )
    serializer_class = LegalCaseSerializer
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ('legal_case_number', 'police_case', 'court_case')
    ordering_fields = ['id', 'legal_case_number', 'form_entered_by', ]
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
    
    def post_process(self, request, form_data):
        validate = ValidateForm(form_data.form, form_data, False, mode="retrieve")
        validate.validate()
        form_data.form_object.missing_data_count = len(validate.warnings)
        form_data.form_object.save()
            
    

