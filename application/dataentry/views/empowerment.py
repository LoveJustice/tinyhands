from rest_framework import filters as fs
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from dataentry.models import BorderStation, Empowerment, UserLocationPermission
from dataentry.serializers import EmpowermentSerializer
from rest_api.authentication import HasPostPermission, HasPutPermission, HasDeletePermission

class EmpowermentViewSet(viewsets.ModelViewSet):
    queryset = Empowerment.objects.all()
    serializer_class = EmpowermentSerializer
    permission_classes = (IsAuthenticated, HasPostPermission, HasPutPermission, HasDeletePermission)
    post_permissions_required = []
    put_permissions_required = []
    delete_permissions_required = []
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ('station__station_name','station__operating_country__name','lines_crossed')
    ordering_fields = ('date_time_entered_into_system', 'station__station_name', 'station__operating_country__name', 'lines_crossed')
    ordering = ('date_time_entered_into_system',)
                
    
    def retrieve_blank(self, request, station_id):
        station = BorderStation.objects.get(id=station_id)
        emp = Empowerment()
        emp.station = station
        
        serializer = EmpowermentSerializer(emp)
        return Response(serializer.data)
    
    def create(self, request):
        account_id = self.request.user.id
        perm_list = UserLocationPermission.objects.filter(account__id=account_id, permission__permission_group='EMP', permission__action='ADD')
        if len(perm_list) == 0:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            return viewsets.ModelViewSet.create(self, request)
    
    def retrieve(self, request, pk):
        account_id = self.request.user.id
        perm_list = UserLocationPermission.objects.filter(account__id=account_id, permission__permission_group='EMP', permission__action='VIEW')
        emp = Empowerment.objects.get(id=pk)
        if not UserLocationPermission.has_permission_in_list(perm_list, 'EMP', 'VIEW', emp.station.operating_country.id, emp.station.id):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            return viewsets.ModelViewSet.retrieve(self, request, pk)
       
    
    def update(self, request, pk):
        account_id = self.request.user.id
        perm_list = UserLocationPermission.objects.filter(account__id=account_id, permission__permission_group='EMP', permission__action='EDIT')
        emp = Empowerment.objects.get(id=pk)
        if not UserLocationPermission.has_permission_in_list(perm_list, 'EMP', 'EDIT', emp.station.operating_country.id, emp.station.id):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            return viewsets.ModelViewSet.update(self, request, pk)
