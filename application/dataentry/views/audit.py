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
    search_fields = ('form_name',)
    ordering_fields = ('end_date',)
    ordering = ('-end_date',)
    
    def get_queryset(self):
        countries = Country.objects.all()
        include_countries = []
        country = self.request.GET.get('country')
        perm_list = UserLocationPermission.objects.filter(account__id=self.request.user.id, permission__permission_group='AUDIT', permission__action='VIEW')
        for country_entry in countries:
            if country is not None and int(country) != country_entry.id:
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
            
        data_class = audit.get_form().storage.get_form_storage_class()
        candidates_queryset = data_class.objects.filter(station__operating_country=audit.country)
        candidates = []
        for candidate in candidates_queryset:
            candidates.append(candidate)
        
        audit.forms_in_range = len(candidates)
        audit.save()
        
        number_to_sample = int (len(candidates) * audit.percent_to_sample / 100 +0.5)
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
    
    def has_permission(self, account_id, action, country_id):
        perm_list = UserLocationPermission.objects.filter(account__id=account_id, permission__permission_group='AUDIT', permission__action=action)
        return UserLocationPermission.has_permission_in_list(perm_list, 'AUDIT', action, country_id, None)
            
    def create(self, request):
        country_id = int(request.data['country'])
        if not self.has_permission(self.request.user.id, 'ADD', country_id):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = AuditSerializer(data=request.data)
        if serializer.is_valid():
            audit = serializer.save()
            self.create_samples(audit)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk):
        audit = Audit.objects.get(id=pk)
        if not self.has_permission(self.request.user.id, 'EDIT', audit.country.id):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = AuditSerializer(audit, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update_notes(self, request, pk):
        audit = Audit.objects.get(id=pk)
        if not self.has_permission(self.request.user.id, 'SUBMIT_SAMPLE', audit.country.id):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        audit.notes = request.data['notes']
        audit.save()
        serializer = AuditSerializer(audit)
        return Response(serializer.data)
        
        

class AuditSampleViewSet(viewsets.ModelViewSet):
    serializer_class = AuditSampleSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ('id',)
    ordering_fields = ('id','form_number')
    ordering = ('id',)
    
    def has_permission(self, account_id, action, country_id):
        perm_list = UserLocationPermission.objects.filter(account__id=account_id, permission__permission_group='AUDIT', permission__action=action)
        return UserLocationPermission.has_permission_in_list(perm_list, 'AUDIT', action, country_id, None)
    
    def get_queryset(self):
        audit_id = self.request.GET.get('audit_id')
        completed = self.request.GET.get('completed')
        if audit_id is not None:
            queryset = AuditSample.objects.filter(audit__id=audit_id)
        else:
            queryset = AuditSample.objects.all()
        if completed is not None:
            if completed == 'true':
                queryset = queryset.filter(completion_date__isnull=False)
            else:
                queryset = queryset.filter(completion_date__isnull=True)
        return queryset
    
    def update(self, request, pk):
        audit_sample = AuditSample.objects.get(id=pk)
        if not self.has_permission(self.request.user.id, 'SUBMIT_SAMPLE', audit_sample.audit.country.id):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer=AuditSampleSerializer(audit_sample, request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    