from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters as fs
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.db.models import Q

from dataentry.models import Permission, UserLocationPermission, Country, BorderStation
from accounts.models import Account
from dataentry.serializers import PermissionSerializer, UserLocationPermissionSerializer, CountrySerializer, BorderStationSerializer, UserLocationPermissionListSerializer

class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ('permission_group','action')
    ordering_fields = ('permission_group', 'action')
    ordering = ('permission_group','action')
    
class UserLocationPermissionViewSet(viewsets.ModelViewSet):
    queryset = UserLocationPermission.objects.all()
    serializer_class = UserLocationPermissionSerializer
    permission_classes = [IsAuthenticated]
    
    def user_permissions(self, request, pk):
        results = self.queryset.filter(account__id=pk)
        
        serializer = UserLocationPermissionSerializer(results, many=True, context={'request': request})
        return Response(serializer.data)
    
    def update_account_permission (self, pk):
        account_perms = Permission.objects.filter(account_permission_name__isnull=False)
        user_perms = UserLocationPermission.objects.filter(account=pk).filter(country__isnull=True).filter(station__isnull=True)
        the_account = Account.objects.get(id=pk)
        for account_perm in account_perms:
            value = False;
            for user_perm in user_perms:
                if account_perm.id == user_perm.permission.id:
                    value = True
                    break
            
            setattr(the_account, account_perm.account_permission_name, value)
        
        the_account.save();
                
    
    def update_permissions(self, request, pk):
        data = JSONParser().parse(request)
        if 'permission_id' in data:
            permission_id = int(data['permission_id'])
        elif 'permission_group' in data:
            permission_group = data['permission_group']
            permission_id = None
        else:
            permission_group = None
            permission_id = None
        
        user_permissions = UserLocationPermission.objects.filter(account__id = request.user.id)
            
        permission_list = data['permissions']
        new_permissions = []
        for perm_data in permission_list:
            serializer = UserLocationPermissionSerializer(data=perm_data)
            if serializer.is_valid():
                perm_obj = serializer.create_local()
                new_permissions.append(perm_obj)
        
        issues = UserLocationPermission.check_valid_permission_set(pk, new_permissions, permission_id, permission_group)
        if len(issues) > 0:
            code = status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            code = UserLocationPermission.update_permission_set (pk, new_permissions, permission_id, permission_group, user_permissions)
            if code == status.HTTP_200_OK:
                self.update_account_permission(pk)
            
        return Response({"data": data}, code)
    
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
    
    def user_countries(self, request, pk):
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
    
    def user_permission_list(self, request):
        
        if 'station_id' in request.GET:
            tmp = int(request.GET['station_id'])
            station = BorderStation.objects.get(id=tmp)
            perms = self.queryset.filter(Q(country__isnull=True) & Q(station__isnull=True) | Q(country__id=station.operating_country.id) | Q(station__id=tmp))
        elif 'country_id' in request.GET:
            tmp = int(request.GET['country_id'])
            perms = self.queryset.filter(Q(country__isnull=True) & Q(station__isnull=True) | Q(country__id=tmp))
        else:
            perms = self.queryset.filter(Q(country__isnull=True) & Q(station__isnull=True))
        
        perms = perms.order_by('account__first_name', 'account__last_name', 'account__id')
        
        last_id = None
        working = None
        results = []
        for perm in perms:
            if working is None or last_id != perm.account.id:
                if working is not None:
                    results.append(working)
                working = {
                    'account_id' : perm.account.id,
                    'name' : perm.account.first_name + " " + perm.account.last_name,
                    'permissions':[]
                }
                last_id = perm.account.id
                
            entry = {'id' : perm.permission_id}
            if perm.station is not None:
                entry['level'] = 'S'
            elif perm.country is not None:
                entry['level'] = 'C'
            else:
                entry['level'] = 'G'
            working['permissions'].append(entry)
        
        if working is not None:
            results.append(working)

        serializer = UserLocationPermissionListSerializer(results, many=True, context={'request': request})   
        return Response(serializer.data) 
                    