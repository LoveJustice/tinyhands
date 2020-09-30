import random

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import filters as fs
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from dataentry.models import Audit, AuditSample, Country, UserLocationPermission
from dataentry.serializers import AuditSerializer, AuditSampleSerializer
from rest_api.authentication import HasPostPermission, HasPutPermission, HasDeletePermission

class AuditViewSet(viewsets.ModelViewSet):
    serializer_class = AuditSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ('form__form_name',)
    ordering_fields = ('end_date',)
    ordering = ('end_date',)
    
    def get_queryset(self):
        countries = Country.objects.all()
        include_countries = []
        country = self.request.GET.get('country')
        perm_list = UserLocationPermission.objects.filter(account__id=self.request.user.id, permission__permission_group='AUDIT', permission__action='VIEW')
        for country_entry in countries:
            if country is not None and country != country_entry.id:
                continue
            if UserLocationPermission.has_permission_in_list(perm_list, 'AUDIT', 'VIEW', country_entry.id, None):
                include_countries.append(country_entry)
            
        queryset = Audit.objects.filter(country__in=include_countries)
       
        form_type = self.request.GET.get('form_type')
        if country is not None:
            queryset = queryset.filter(country__id=country)
        if form_type is not None:
             queryset = queryset.filter(form__form_type__id=form_type)
        return queryset
    
    def create_samples(self, audit):
        results = {}
        for section in audit.template:
            results[section['name']] = None
            
        data_class = audit.form.storage.get_form_storage_class()
        candidates_queryset = data_class.objects.filter(station__operating_country=audit.country)
        candidates = []
        for candidate in candidates_queryset:
            candidates.append(candidate)
        
        number_to_sample = int (len(candidates) * audit.percent_to_sample / 100 +0.5)
        print('number of candidates', len(candidates), 'percent', audit.percent_to_sample, 'number to sample', number_to_sample)
        random.seed()
        for idx in range(0,number_to_sample):
            selected = random.randint(0,len(candidates)-1)
            sample = candidates.pop(selected)
            audit_sample = AuditSample()
            audit_sample.audit = audit
            audit_sample.form_id = sample.id
            audit_sample.form_number = sample.get_key()
            audit_sample.results = results
            audit_sample.save()
            
    def create(self, request):
        serializer = AuditSerializer(data=request.data)
        if serializer.is_valid():
            audit = serializer.save()
            self.create_samples(audit)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AuditSampleViewSet(viewsets.ModelViewSet):
    serializer_class = AuditSampleSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ('id',)
    ordering_fields = ('id',)
    ordering = ('id',)
    
    def get_queryset(self):
        audit_id = self.request.GET.get('audit_id')
        if audit_id is not None:
            queryset = AuditSample.objects.filter(audit__id=audit_id)
        else:
            queryset = AuditSample.objects.all()
        return queryset