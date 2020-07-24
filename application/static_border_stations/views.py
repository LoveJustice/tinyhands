import pytz

from rest_framework import viewsets
from rest_framework.decorators import list_route, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django_filters import rest_framework as filters

from dataentry.models import BorderStation
from dataentry.serializers import BorderStationSerializer
from rest_api.authentication_expansion import HasPermission, HasPostPermission, HasPutPermission
from static_border_stations.models import Staff, CommitteeMember, Location
from static_border_stations.serializers import StaffSerializer, CommitteeMemberSerializer, LocationSerializer


class BorderStationViewSet(viewsets.ModelViewSet):
    queryset = BorderStation.objects.all()
    serializer_class = BorderStationSerializer
    permission_classes = (IsAuthenticated, HasPermission, HasPostPermission, HasPutPermission)
    permissions_required = [{'permission_group':'STATIONS', 'action':'VIEW'},]
    post_permissions_required = [{'permission_group':'STATIONS', 'action':'ADD'},]
    put_permissions_required = [{'permission_group':'STATIONS', 'action':'EDIT'},]
    
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


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def get_station_id(request):
    code = request.GET['code']
    if code == '':
        return Response(-1)
    else:
        station = BorderStation.objects.filter(station_code=code)
        if len(station) > 0:
            return Response(station[0].id)
        else:
            return Response(-1)


class BorderStationRestAPI(viewsets.ModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('border_station',)
    permission_classes = (IsAuthenticated, HasPermission, HasPostPermission, HasPutPermission)
    permissions_required = [{'permission_group':'STATIONS', 'action':'VIEW'},]
    post_permissions_required = [{'permission_group':'STATIONS', 'action':'ADD'},]
    put_permissions_required = [{'permission_group':'STATIONS', 'action':'EDIT'},]


class LocationViewSet(BorderStationRestAPI):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    ordering = ('name',)
    
    def retrieve_border_station_locations(self, request, *args, **kwargs):
        """
            retrieve all locations for a particular border_station
        """
        self.object_list = self.filter_queryset(self.get_queryset().filter(border_station=self.kwargs['pk'], active=True)).order_by('name')
        serializer = self.get_serializer(self.object_list, many=True)
        return Response(serializer.data)


class CommitteeMemberViewSet(BorderStationRestAPI):
    queryset = CommitteeMember.objects.all()
    serializer_class = CommitteeMemberSerializer


class StaffViewSet(BorderStationRestAPI):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    ordering = ('email',)

    def retrieve_border_station_staff(self, request, *args, **kwargs):
        """
            retrieve all the staff for a particular border_station
        """
        self.object_list = self.filter_queryset(self.get_queryset().filter(border_station=self.kwargs['pk'], last_date__isnull=True))
        serializer = self.get_serializer(self.object_list, many=True)
        return Response(serializer.data)

class TimeZoneViewSet(viewsets.ViewSet):
    def get_time_zones(self, request):
        return Response(pytz.all_timezones)
