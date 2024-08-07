import logging

from rest_framework import filters as fs
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from dataentry.models import BorderStation, Country, Gospel, UserLocationPermission
from dataentry.serializers import GospelSerializer
from rest_api.authentication import HasPostPermission, HasPutPermission, HasDeletePermission


class GospelViewSet(viewsets.ModelViewSet):
    queryset = Gospel.objects.all()
    serializer_class = GospelSerializer
    permission_classes = (IsAuthenticated, HasPostPermission, HasPutPermission, HasDeletePermission)
    post_permissions_required = []
    put_permissions_required = []
    delete_permissions_required = []
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ('station__station_name','station__operating_country__name', 'full_name')
    ordering_fields = ('date_time_entered_into_system', 'station__station_name', 'station__operating_country__name', 'full_name')
    ordering = ('date_time_entered_into_system',)
                
    def get_queryset(self):
        countries = Country.objects.all()
        include_countries = []
        country_ids = self.request.GET.get('country_ids')
        perm_list = UserLocationPermission.objects.filter(account__id=self.request.user.id, permission__permission_group='GSP', permission__action='VIEW')
        for country_entry in countries:
            if country_ids is not None and str(country_entry.id) not in country_ids:
                continue
            if UserLocationPermission.has_permission_in_list(perm_list, 'GSP', 'VIEW', country_entry.id, None):
                include_countries.append(country_entry)
        
        queryset = Gospel.objects.filter(station__operating_country__in=include_countries)
       
        return queryset
    
    def retrieve_blank(self, request, station_id):
        station = BorderStation.objects.get(id=station_id)
        gsp = Gospel()
        gsp.station = station
        
        serializer = GospelSerializer(gsp)
        return Response(serializer.data)
    
    def create(self, request):
        account_id = self.request.user.id
        perm_list = UserLocationPermission.objects.filter(account__id=account_id, permission__permission_group='GSP', permission__action='ADD')
        if len(perm_list) == 0:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            return viewsets.ModelViewSet.create(self, request)
    
    def retrieve(self, request, pk):
        account_id = self.request.user.id
        perm_list = UserLocationPermission.objects.filter(account__id=account_id, permission__permission_group='GSP', permission__action='VIEW')
        gsp = Gospel.objects.get(id=pk)
        if not UserLocationPermission.has_permission_in_list(perm_list, 'GSP', 'VIEW', gsp.station.operating_country.id, gsp.station.id):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            return viewsets.ModelViewSet.retrieve(self, request, pk)
       
    
    def update(self, request, pk):
        account_id = self.request.user.id
        perm_list = UserLocationPermission.objects.filter(account__id=account_id, permission__permission_group='GSP', permission__action='EDIT')
        gsp = Gospel.objects.get(id=pk)
        if not UserLocationPermission.has_permission_in_list(perm_list, 'GSP', 'EDIT', gsp.station.operating_country.id, gsp.station.id):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            return viewsets.ModelViewSet.update(self, request, pk)
