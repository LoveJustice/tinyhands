import pytz
import datetime

from rest_framework import status
from rest_framework import serializers
from rest_framework import filters as fs
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from templated_email import send_templated_mail

from dataentry.serialize_form import FormDataSerializer
from .base_form import BaseFormViewSet, BorderStationOverviewSerializer
from dataentry.serializers import IncidentSerializer

from dataentry.form_data import Form, FormData
from dataentry.models import Person, UserLocationPermission, Incident, LocationForm

class LfListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    lf_number = serializers.SerializerMethodField(read_only=True)
    merged_place = serializers.CharField()
    merged_place_kind = serializers.CharField()
    address = serializers.SerializerMethodField(read_only=True)
    station = BorderStationOverviewSerializer()
    form_name = serializers.SerializerMethodField(read_only=True)
    incident = serializers.SerializerMethodField(read_only=True)
    
    perm_group_name = 'LF'
    
    def get_lf_number(self, obj):
        return obj.lf_number
    
    def get_address(self, obj):
        address = ''
        if obj.merged_address is not None and 'address' in obj.merged_address:
            address = obj.merged_address['address']
        return address
    
    def get_form_name(self, obj):
        forms = Form.objects.filter(form_type__name='LF', stations__id=obj.station.id)
        if len(forms) > 0:
            return forms[0].form_name
        else:
            return None
    
    def get_incident(self, obj):
        
        incident_number = obj.lf_number
        for idx in range(3,len(obj.lf_number)):
            if obj.lf_number[idx] != '_' and (obj.lf_number[idx] < '0' or obj.lf_number[idx] > '9'):
                incident_number = obj.lf_number[0:idx]
                break
        try:
            incident = Incident.objects.get(incident_number=incident_number)
            return incident.id
        except ObjectDoesNotExist:
            return None
    
class LfFormViewSet(BaseFormViewSet):
    parser_classes = (MultiPartParser,FormParser,JSONParser)
    permission_classes = (IsAuthenticated, )
    serializer_class = LfListSerializer
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ['lf_number',]
    ordering_fields = [
        'id', 'lf_number', 'merged_place', 'merged_place_kind']
    ordering = ('-lf_number')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return LfListSerializer
        else:
            return FormDataSerializer
    
    def get_serializer_context(self): 
        return self.serializer_context
    
    def get_perm_group_name(self):
        return 'LF'
    
    def get_form_type_name(self):
        return 'LF'
    
    def get_element_paths(self):
        return [
            {
                'element':'scanned',
                'path':'lf_attachments/'
            }]
    
    def get_list_field_names(self):
        return ['id']
        
    def get_empty_queryset(self):
        return LocationForm.objects.none()
    
    def filter_key(self, queryset, search):
        return queryset.filter(lf_number__contains=search)
    
    def post_create(self, form_data):
        lf_number = form_data.form_object.lf_number
        incident_number = ''
        for idx in range(len(lf_number)-1,2,-1):
            if lf_number[idx] >= '0' and lf_number[idx] <= '9':
                incident_number = lf_number[0:idx+1]
                break
        
        incident = Incident.objects.get(incident_number=incident_number)
        form_data.form_object.incidents.add(incident)
    
    def custom_create_blank(self, form_object):
        form_object.victim = Person()
    
    def get_associated_incidents(self, request, pk):
        lf = LocationForm.objects.get(id=pk)
        associated_incidents = lf.associated_incidents.all();
        serializer = IncidentSerializer(associated_incidents, many=True, context={'request': request})
        return Response(serializer.data)
    
    def set_associated_incidents(self, request, pk):
        lf = LocationForm.objects.get(id=pk)
        add_incident = []
        for incident_id in request.data:
            incident = Incident.objects.get(id=incident_id)
            add_incident.append(incident)
        
        lf.associated_incidents.clear()
        
        for incident in add_incident:
            lf.associated_incidents.add(incident)
        
        return Response('')
                

   
    



