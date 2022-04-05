import pytz

from rest_framework import viewsets
from rest_framework.decorators import list_route, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django_filters import rest_framework as filters

from dataentry.models import BorderStation
from dataentry.serializers import BorderStationSerializer
from rest_api.authentication_expansion import HasPermission, HasPostPermission, HasPutPermission
from static_border_stations.models import Staff, CommitteeMember, Location, WorksOnProject
from static_border_stations.serializers import StaffSerializer, CommitteeMemberSerializer, LocationSerializer


class BorderStationViewSet(viewsets.ModelViewSet):
    queryset = BorderStation.objects.all()
    serializer_class = BorderStationSerializer
    permission_classes = (IsAuthenticated, HasPermission, HasPostPermission, HasPutPermission)
    permissions_required = [{'permission_group':'PROJECTS', 'action':'VIEW'},]
    post_permissions_required = [{'permission_group':'PROJECTS', 'action':'ADD'},]
    put_permissions_required = [{'permission_group':'PROJECTS', 'action':'EDIT'},]
    
    @list_route()
    def list_all(self, request):
        border_stations = BorderStation.objects.all().order_by('station_name')
        country_param = request.query_params.get('operating_country', None)
        if country_param is not None:
            border_stations = border_stations.filter(operating_country=country_param)
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
    permissions_required = [{'permission_group':'PROJECTS', 'action':'VIEW'},]
    post_permissions_required = [{'permission_group':'PROJECTS', 'action':'ADD'},]
    put_permissions_required = [{'permission_group':'PROJECTS', 'action':'EDIT'},]


class LocationViewSet(BorderStationRestAPI):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    ordering = ('name',)
    
    def retrieve_border_station_locations(self, request, *args, **kwargs):
        """
            retrieve all locations for a particular border_station
        """
        station = BorderStation.objects.get(id=self.kwargs['pk'])
        Location.get_or_create_other_location(station)
        Location.get_or_create_leave_location(station)
        self.object_list = self.filter_queryset(self.get_queryset().filter(border_station=station))
        if request.GET.get('include_inactive') is None:
            self.object_list = self.object_list.filter(active=True)
        if request.GET.get('location_type') is not None:
            self.object_list = self.object_list.filter(location_type=request.GET.get('location_type'))
        self.object_list = self.object_list.order_by('-active', 'name')
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
        self.object_list = self.filter_queryset(self.get_queryset().filter(border_station=self.kwargs['pk']))
        if request.GET.get('include_inactive') is None:
            self.object_list = self.object_list.filter(last_date__isnull=True)
        serializer = self.get_serializer(self.object_list, many=True)
        return Response(serializer.data)
    
    def getStaff(self, include_inactive, include_financial):
        staff = []
        
        works_on_list = WorksOnProject.objects.filter(border_station__id=self.kwargs['pk'])
        for works_on in works_on_list:
            if works_on.staff not in staff and (include_inactive or works_on.staff.last_date is None):
                staff.append(works_on.staff)
        if include_financial:
            financial_list = self.filter_queryset(self.get_queryset().filter(border_station=self.kwargs['pk']))
            for financial in financial_list:
                if financial not in staff and (include_inactive or financial.last_date is None):
                    staff.append(financial)
        
        return staff
    
    def retrieve_border_station_staff(self, request, *args, **kwargs):
        """
            retrieve all the staff for a particular border_station
        """
        staff = []
        if request.GET.get('include_inactive') is not None:
            include_inactive = True
        else:
            include_inactive = False
        if request.GET.get('include_financial'):
            include_financial = True
        else:
            include_financial = False
        
        staff = self.getStaff(include_inactive, include_financial)
                    
        serializer = self.get_serializer(staff, many=True)
        return Response(serializer.data)
    
    def getValue(self, data, path):
        current = data
        for piece in path:
            if piece not in current:
                return None
            current = current[piece]
        
        return current
    
    def update_border_station_staff_work(self, request, pk):
        print ('request.data', request.data)
        for staff in request.data:
            staff_id = self.getValue(staff, ['id'])
            works_on = self.getValue(staff, ['works_on'])
            if (staff_id is None or works_on is None):
                continue
            for work_element in works_on:
                financial_id = self.getValue(work_element, ['financial', 'project_id'])
                percent = self.getValue(work_element, ['percent'])
                work_id = self.getValue(work_element, ['works_on', 'project_id'])
                print('values', pk, staff_id, financial_id, percent, work_id)
                id = self.getValue(work_element, ['id'])
                if financial_id is None or percent is None or work_id is None:
                    print('Bail 1')
                    continue
                if str(financial_id) != str(pk):
                    print('Does not match pk', pk)
                    continue
                
                staff = Staff.objects.get(id=staff_id)
                border_station = BorderStation.objects.get(id=work_id)
                if id is None:
                    works_on_project = WorksOnProject()
                else:
                    works_on_project = WorksOnProject.objects.get(id=id)
                
                works_on_project.staff = staff
                works_on_project.work_percent = percent
                works_on_project.border_station = border_station
                print('saving', works_on_project, staff.id, works_on_project.work_percent,  works_on_project.border_station.id)
                works_on_project.save()
        
        staff = self.getStaff(False, True)
                    
        serializer = self.get_serializer(staff, many=True)
        return Response(serializer.data)

class TimeZoneViewSet(viewsets.ViewSet):
    def get_time_zones(self, request):
        return Response(pytz.all_timezones)
