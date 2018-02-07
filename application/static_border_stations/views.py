from rest_framework import viewsets
from rest_framework.decorators import list_route, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django_filters import rest_framework as filters

from dataentry.models import BorderStation, UserLocationPermission
from dataentry.serializers import BorderStationSerializer
from static_border_stations.models import Staff, CommitteeMember, Location
from static_border_stations.serializers import StaffSerializer, CommitteeMemberSerializer, LocationSerializer


class BorderStationViewSet(viewsets.ModelViewSet):
    queryset = BorderStation.objects.all()
    serializer_class = BorderStationSerializer
    permission_classes = (IsAuthenticated, )
    
    @list_route()
    def list_all(self, request):
        border_stations = BorderStation.objects.all().order_by('station_name')
        open_param = request.query_params.get('open', None)
        if open_param in ['True', 'true']:
            border_stations = border_stations.filter(open=True)
        elif open_param in ['False', 'false']:
            border_stations = border_stations.filter(open=False)
        serializer = self.get_serializer(border_stations, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        station = BorderStation.objects.filter(id=self.kwargs['pk'])
        if len(station) < 1:
            return Response({"message": "Border Station not found"}, status.HTTP_204_NO_CONTENT)
        elif not UserLocationPermission.has_session_permission(request, 'STATIONS', 'VIEW', station[0].operating_country.id, station[0].id):
            return Response({"message": "You are not authorized to view this Border Station"}, status.HTTP_401_UNAUTHORIZED)
        return super(BorderStationViewSet, self).retrieve(request, args, kwargs)
    
    def destroy(self, request, *args, **kwargs):
        return Response({"message": "Border Station may not be deleted"}, status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def get_station_id(request):
    code = request.GET['code']
    if code == '':
        return Response(-1)
    else:
        station = BorderStation.objects.filter(station_code=code)
        if len(station) > 0:
            if not UserLocationPermission.has_session_permission(request, 'STATIONS', 'VIEW', station[0].operating_country.id, station[0].id):
                return Response({"message": "You are not authorized to view this Border Station"}, status.HTTP_401_UNAUTHORIZED)
            return Response(station[0].id)
        else:
            return Response(-1)


class BorderStationRestAPI(viewsets.ModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('border_station',)
    permission_classes = (IsAuthenticated, )


class LocationViewSet(BorderStationRestAPI):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    ordering = ('id',)
    
    def retrieve_border_station_locations(self, request, *args, **kwargs):
        """
            retrieve all locations for a particular border_station
        """
        self.object_list = self.filter_queryset(self.get_queryset().filter(border_station=self.kwargs['pk']))
        if len(self.object_list) > 0 and not UserLocationPermission.has_session_permission(request, 'STATIONS', 'VIEW', self.object_list[0].border_station.operating_country.id, self.object_list[0].border_station.id):
            return Response({"message": "You are not authorized to view committee members for this Border Station"}, status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(self.object_list, many=True)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        return Response({"message": "Location may not be deleted"}, status.HTTP_405_METHOD_NOT_ALLOWED)

class CommitteeMemberViewSet(BorderStationRestAPI):
    queryset = CommitteeMember.objects.all()
    serializer_class = CommitteeMemberSerializer
    ordering = ('id',)
    
    def destroy(self, request, *args, **kwargs):
        return Response({"message": "Committee member may not be deleted"}, status.HTTP_405_METHOD_NOT_ALLOWED)
        

class StaffViewSet(BorderStationRestAPI):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    ordering = ('id',)

    def retrieve_border_station_staff(self, request, *args, **kwargs):
        """
            retrieve all the staff for a particular border_station
        """
        self.object_list = self.filter_queryset(self.get_queryset().filter(border_station=self.kwargs['pk']))
        if len(self.object_list) > 0 and not UserLocationPermission.has_session_permission(request, 'STATIONS', 'VIEW', self.object_list[0].border_station.operating_country.id, self.object_list[0].border_station.id):
            return Response({"message": "You are not authorized to view committee members for this Border Station"}, status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(self.object_list, many=True)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        return Response({"message": "Staff member may not be deleted"}, status.HTTP_405_METHOD_NOT_ALLOWED)
