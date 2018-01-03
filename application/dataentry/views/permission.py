from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters as fs
from rest_framework.parsers import JSONParser

from dataentry.models import Permission, UserLocationPermission, Country, BorderStation
from dataentry.serializers import PermissionSerializer, UserLocationPermissionSerializer, CountrySerializer, BorderStationSerializer

class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    #permission_classes = [IsAuthenticated]
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ('permission_group','action')
    ordering_fields = ('permission_group', 'action')
    ordering = ('permission_group','action')
    
class UserLocationPermissionViewSet(viewsets.ModelViewSet):
    queryset = UserLocationPermission.objects.all()
    serializer_class = UserLocationPermissionSerializer
    #permission_classes = [IsAuthenticated]
    
    def user_permissions(self, request, pk):
        results = self.queryset.filter(account__id=pk)
        if 'country_id' in request.GET:
            tmp = int(request.GET['country_id'])
            results = results.filter(country__id=tmp)
          
        if 'station_id' in request.GET:
            tmp = int(request.GET['station_id'])
            results = results.filter(station__id=tmp)
        
        if 'permission_id' in request.GET:
            tmp = int(request.GET['permission_id'])
            results = results.filter(permission__id=tmp)
        
        if 'permission_group' in request.GET:
            tmp = request.GET['permission_group']
            results = results.filter(permission__permission_group=tmp)
        
        if 'action' in request.GET:
            tmp = request.GET['action']
            results = results.filter(permission__action=tmp)
        
        serializer = UserLocationPermissionSerializer(results, many=True, context={'request': request})
        return Response(serializer.data)
    
    def update_permissions(self, request, pk):
        txt = 'success!'
        data = JSONParser().parse(request)
        new_permissions = []
        for perm_data in data:
            serializer = UserLocationPermissionSerializer(data=perm_data)
            if serializer.is_valid():
                perm_obj = serializer.create_local()
                new_permissions.append(perm_obj)
            else:
                print "is not valid"
        
        issues = UserLocationPermission.check_valid_permission_set(pk, new_permissions)
        if len(issues) > 0:
            txt = issues[0]
            
        return Response({"message": txt})
    
    def effective_query(self, request, pk):
        results = self.queryset.filter(account__id=pk)        

        if 'permission_id' in request.GET:
            tmp = int(request.GET['permission_id'])
            results = results.filter(permission__id=tmp)
        
        if 'permission_group' in request.GET:
            tmp = request.GET['permission_group']
            results = results.filter(permission__permission_group=tmp)
        
        if 'action' in request.GET:
            tmp = request.GET['action']
            results = results.filter(permission__action=tmp)
            
        return results;
    
    def effective_permissions(self, request, pk):
        results = self.effective_query(request, pk)
        
        if 'station_id' in request.GET:
            # when station is specified, include global permissions and permissions for the station's country as well as those for the station
            tmp = int(request.GET['station_id'])
            the_station = BorderStation.objects.get(id=tmp)
            results = results.filter(station__id=tmp) | results.filter(country__id=the_station.id) | results.filter(country=None).filter(station=None)        
        elif 'country_id' in request.GET:
            # when country is specified, include global permissions as well as those for the country
            tmp = int(request.GET['country_id'])
            results = results.filter(country__id=tmp) | results.filter(country=None).filter(station=None)
        
        serializer = UserLocationPermissionSerializer(results, many=True, context={'request': request})
        return Response(serializer.data, pk)
    
    def user_countries(self, request):
        perms = self.effective_query(request, pk)
        results = None
        
        for perm in perms.iterator():
            if perm.country is None and perm.station is None:
                results = Country.objects.all()
                break
            
            if perm.country is not None:
                if results is not None:
                    results |= Country.objects.filter(id=perm.country.id)
                else:
                    results = Country.objects.filter(id=perm.country.id)
            
            if perm.station is not None:
                if results is not None:
                    results |= Country.objects.filter(id=perm.station.operating_country.id)
                else:
                    results = Country.objects.filter(id=perm.station.operating_country.id)       
            
        serializer = CountrySerializer(results, many=True, context={'request': request})
        return Response(serializer.data)
    
    def user_stations(self, request, pk):
        perms = self.effective_query(request, pk)
        results = None
        
        if 'country_id' in request.GET:
            tmp = int(request.GET['country_id'])
            stations = BorderStation.objects.filter(operating_country__id = tmp)
        else:
            stations = BorderStation.objects.all()
        
        for perm in perms.iterator():
            if perm.country is None and perm.station is None:
                results = stations
                break
            
            if perm.country is not None:
                if results is not None:
                    results |= stations.filter(operating_country__id = perm.country.id)
                else:
                    results = stations.filter(operating_country__id = perm.country.id)
            
            if perm.station is not None:
                if results is not None:
                    results |= stations.filter(id = perm.station.id)
                else:
                    results = stations.filter(id = perm.station.id)
        
        serializer = BorderStationSerializer(results, many=True, context={'request': request})
        return Response(serializer.data)
                    