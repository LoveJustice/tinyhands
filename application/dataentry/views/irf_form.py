import json
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import filters as fs

from braces.views import LoginRequiredMixin
from accounts.mixins import PermissionsRequiredMixin

from django.views.generic import CreateView
from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet
from dataentry.serialize_form import FormDataSerializer
from dataentry.serializers import CountrySerializer

from dataentry.form_data import Form, FormData
from dataentry.models import BorderStation, Country, IrfCore, UserLocationPermission

class BorderStationOverviewSerializer(serializers.ModelSerializer):
    operating_country = CountrySerializer()
    class Meta:
        fields = [
            'id',
            'station_code',
            'station_name',
            'operating_country',
        ]
        model = BorderStation

class IrfListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    irf_number = serializers.CharField()
    number_of_victims = serializers.IntegerField()
    number_of_traffickers = serializers.IntegerField()
    staff_name = serializers.CharField()
    date_time_of_interception = serializers.DateTimeField()
    date_time_entered_into_system = serializers.DateTimeField()
    date_time_last_updated = serializers.DateTimeField()
    station = BorderStationOverviewSerializer()
    can_view = serializers.SerializerMethodField(read_only=True)
    can_edit = serializers.SerializerMethodField(read_only=True)
    can_delete = serializers.SerializerMethodField(read_only=True)
    can_approve = serializers.SerializerMethodField(read_only=True)
    
    perm_group_name = 'IRF'
    
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

class IrfFormViewSet(viewsets.ModelViewSet):
    serializer_class = IrfListSerializer
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ('irf_number',)
    ordering_fields = (
        'irf_number', 'staff_name', 'number_of_victims', 'number_of_traffickers', 'date_time_of_interception',
        'date_time_entered_into_system', 'date_time_last_updated',)
    ordering = ('-date_time_of_interception',)
    form_type_name = 'IRF'
    perm_group_name = 'IRF'
    
    def get_serializer_context(self):
        return self.serializer_context
    
    def get_queryset(self):
        in_country = self.request.GET.get('country_ids')
        status = self.request.GET.get('status', 'approved')
        search = self.request.GET.get('search')
        
        countries = Country.objects.all()
        all_country_list = []
        for country in countries:
            all_country_list.append(country.id)
        
        country_list = []
        if in_country is not None and in_country != '':
            # client provided a list of countries to consider
            for cntry in in_country.split(','):
                country_list.append(int(cntry))
        else:
            # client did not provide a list - so consider all countries
           country_list = all_country_list
        
        account_id = self.request.user.id
        #account_id = 10023
        
        #Get the account's IRF permissions and store them so they can be referenced by the serializer
        perm_list = UserLocationPermission.objects.filter(account__id=account_id, permission__permission_group=self.perm_group_name).exclude(permission__action='CREATE')
        self.serializer_context = {'perm_list':perm_list}
        
        # selected_countries to contain the list of country_ids where the user has VIEW permission for at
        # least one station
        selected_countries = []
        for perm in perm_list:
            if perm.country is None and perm.station is None:
                selected_countries = country_list
                break
            
            if perm.country is not None:
                id = perm.country.id
                if id in country_list and id not in selected_countries:
                    selected_countries.append(id)
            
            if perm.station is not None:
                id = perm.station.operating_country.id
                if id in country_list and id not in selected_countries:
                    selected_countries.append(id)
        
        # For each selected country where an IRF form exists, query the country IRF table
        # If VIEW permission is country wide, query all IRFs.  Otherwise query based on stations with VIEW permission
        queryset = None
        for country_id in all_country_list:
            form = Form.current_form(self.form_type_name, country_id)
            if form is not None:
                mod = __import__(form.storage.module_name, fromlist=[form.storage.form_model_name])
                form_model = getattr(mod, form.storage.form_model_name)
                
                if country_id in selected_countries:
                    filter_stations= []
                    country_perm_list = perm_list.filter(country=None, station=None)
                    country_perm_list = country_perm_list.union(perm_list.filter(country__id = country_id))
                    country_perm_list = country_perm_list.union(perm_list.filter(station__operating_country__id = country_id))
                    for perm in country_perm_list:
                        if perm.station is None:
                            filter_stations = []
                            break
                        else:
                            filter_stations.append(perm.station)
                        
                    if len(filter_stations):
                        tmp_queryset = form_model.objects.filter(station__in=filter_stations, status=status).only(
                            'id', 'irf_number', 'form_entered_by', 'number_of_victims', 'number_of_traffickers', 'staff_name', 
                            'station', 'date_time_of_interception', 'date_time_entered_into_system',
                            'date_time_last_updated')
                    else:
                        tmp_queryset = form_model.objects.filter(status=status).only(
                            'id', 'irf_number', 'form_entered_by', 'number_of_victims', 'number_of_traffickers', 'staff_name', 
                            'station', 'date_time_of_interception', 'date_time_entered_into_system',
                            'date_time_last_updated')
                    
                    # If query is for in-progress status IRFs, only include IRFs that were entered by the requesters account
                    if status == 'in-progress':
                        tmp_queryset = tmp_queryset.filter(form_entered_by__id=account_id)
                    
                    if search is not None:
                        tmp_queryset = tmp_queryset.filter(irf_number__contains=search)
                    
                    if queryset is None:
                        queryset = tmp_queryset
                    else:
                        queryset = queryset.union(tmp_queryset)
                else:
                    # just in case there are no models on which to do a real query, keep a model to create an empty queryset
                    empty_form_model = form_model
                    
        if queryset is None and empty_form_model is not None:
            queryset = empty_form_model.objects.none()
                
        return queryset
    
    def retrieve(self, request, country_id, pk):
        form = Form.current_form(self.form_type_name, country_id)
        irf = FormData.find_object_by_id(pk, form)
        form_data = FormData(irf, form)
        serializer = FormDataSerializer(form_data)
       
        return Response(serializer.data)

