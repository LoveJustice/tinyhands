import datetime
from dateutil.relativedelta import relativedelta
from rest_framework import viewsets, status
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters as fs
from rest_framework.response import Response
from django.db.models import Value, IntegerField, Q
from django.contrib.contenttypes.models import ContentType

from dataentry.models import BorderStation, IntercepteeCommon, StationStatistics, UserLocationPermission
from dataentry.serializers import CountrySerializer
from budget.models import BorderStationBudgetCalculation, MonthlyDistributionForm, MdfCombined, MdfItem, ProjectRequest, ProjectRequestComment
from budget.serializers import MonthlyDistributionFormSerializer, MdfItemSerializer

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
        
class MdfCombinedSerializer(serializers.ModelSerializer):
    class Meta:
        model = MdfCombined
        fields = ['month_year', 'border_station', 'status', 'date_time_entered', 'date_time_last_updated', 'mdf_type', 'id']
    
    border_station = BorderStationOverviewSerializer(read_only=True)
    mdf_type = serializers.SerializerMethodField(read_only=True)  
    id = serializers.SerializerMethodField(read_only=True)  
    
    def get_mdf_type(self, obj):
        if isinstance(obj.content_object, BorderStationBudgetCalculation):
            return 'budget'
        return 'mdf-pr'
    
    def get_id(self, obj):
            return obj.content_object.id

class MdfCombinedViewSet(viewsets.ModelViewSet):
    queryset = MdfCombined.objects.all()
    serializer_class = MdfCombinedSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ['border_station__station_name', 'border_station__station_code', 'status']
    ordering_fields = ['border_station__station_name', 'border_station__station_code', 'month_year', 'status', 'date_time_entered', 'date_time_last_updated']
    ordering = ['-month_year']
    
    def get_queryset(self):
        border_stations = UserLocationPermission.get_stations_with_permission(self.request.user.id, 'MDF', 'VIEW')
        queryset = MdfCombined.objects.filter(border_station__in=border_stations)
        in_country = self.request.GET.get('country_ids')
        if in_country is not None and in_country != '':
            country_list = []
            for cntry in in_country.split(','):
                country_list.append(int(cntry))
            queryset = queryset.filter(border_station__operating_country__id__in=country_list)   
        
        return queryset

class MonthlyDistributionFormViewSet(viewsets.ModelViewSet):
    queryset = MonthlyDistributionForm.objects.all()
    serializer_class = MonthlyDistributionFormSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ['border_station__station_name', 'border_station__station_code']
    ordering_fields = ['border_station__station_name', 'border_station__station_code', 'month_year', 'date_time_entered', 'date_time_last_updated']
    
    def get_queryset(self):
        queryset = self.queryset
        station_id = self.request.GET.get('station_id')
        if station_id is not None and station_id != '':
            queryset = queryset.filter(border_station__id=station_id)
        status = self.request.GET.get('status')
        if status is not None and status != '':
            queryset = queryset.filter(status=status)
        year = self.request.GET.get('year')
        if year is not None and year != '':
            queryset = queryset.filter(month_year__year=year)
        month = self.request.GET.get('month')
        if month is not None and month != '':
            queryset = queryset.filter(month_year__month=month)
        
        return queryset
    
    def get_new_mdf(self, request, station_id, year, month):
        station =  BorderStation.objects.get(id=station_id)
        if not UserLocationPermission.has_session_permission(request, 'MDF', 'ADD', station.operating_country.id, station.id):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        active_mdfs = MonthlyDistributionForm.objects.filter(border_station=station).exclude(status='Approved')
        if len(active_mdfs) > 0:
            data = {'error':'There is already an active MDF for this project.  Only one active (not Approved) my be present for a project.'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        existing_mdfs = MonthlyDistributionForm.objects.filter(border_station=station, month_year__year=year, month_year__month=month)
        if len(existing_mdfs) > 0:
            data = {'error':'There is already an MDF for this project for the requested year and month'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        
        mdf_date = datetime.datetime(int(year), int(month), 15, tzinfo=datetime.timezone.utc)
        prior_month = mdf_date.date() - relativedelta(months=1)
        
        interceptees = IntercepteeCommon.objects.filter(
                interception_record__station=station,
                interception_record__verified_date__year=prior_month.year,
                interception_record__verified_date__month=prior_month.month,
                person__role='PVOT').exclude(interception_record__verified_evidence_categorization='Should not count as an Intercept')
        
        mdf = MonthlyDistributionForm()
        mdf.border_station = station
        mdf.status = 'Submitted'
        mdf.month_year = mdf_date
        mdf.last_month_number_of_intercepted_pvs = len(interceptees)
        mdf.save()
        
        project_requests = ProjectRequest.objects.filter(override_mdf_project=mdf.border_station, status='Approved')
        for project_request in project_requests:
            mdf.requests.add(project_request)
        project_requests = ProjectRequest.objects.filter(override_mdf_project=mdf.border_station, status='Declined')
        for project_request in project_requests:
            mdf.requests.add(project_request)
        
        request_comments = ProjectRequestComment.objects.filter(mdf__isnull=True, request__override_mdf_project=mdf.border_station)
        for request_comment in request_comments:
            request_comment.mdf = mdf
            request_comment.save()
            try:
                mdf.requests.add(request_comment.request)
            except IntegrityError:
                # request was already added
                pass
        
        serializer = self.serializer_class(mdf)
        return Response(serializer.data)
    
    def approve_mdf(self, request, pk):
        mdf = MonthlyDistributionForm.objects.get(id=pk)
        if not ((status == 'Submitted' and UserLocationPermission.has_session_permission(request, 'MDF', 'INITIAL_REVIEW', station.operating_country.id, station.id)) or
             (status == 'Initial Review' and not UserLocationPermission.has_session_permission(request, 'MDF', 'FINAL_REVIEW', station.operating_country.id, station.id))):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        # Close open discussions
        project_requests = mdf.requests.filter(discussion_status='Open')
        for project_request in project_requests:
            discussion = ProjectRequestDiscussion()
            discussion.request = project_request
            discussion.author = request.user.id
            discussion.text = 'Closed on MDF approval'
            discussion.save()
            project_request.discussion_status = 'Closed'
            project_request.save()
        
        if UserLocationPermission.has_session_permission(request, 'MDF', 'FINAL_REVIEW', station.operating_country.id, station.id):
            mdf.status = 'Approved'
            project_requests = mdf.requests.all()
            for project_request in project_requests:
                if project_request.status == 'Declined':
                    project_request.status = 'Declined-Approved'
                    project_request.save()
                elif project_request == 'Approved' and not project_request.monthly:
                    project_request.status = 'Approved-Completed'
                    project_request.save()
            self.update_stats(mdf)
        else:
            mdf.status = 'Initial Review'
        mdf.save()
        serializer = self.serializer_class(mdf)
        return Response(serializer.data)
    
    def update_stats(self, the_mdf):
        # get a set of all projects on the MDF
        request_projects = the_mdf.requests.all().values_list('project', flat=True)
        item_projects = the_mdf.mdfitems_set.all().value_list('work_project', flat=True)
        projects = set(request_projects + item_projects)
        
        year_month = the_mdf.month_year.year * 100 + the_mdf.month_year.month
        
        for project in projects:
            stats = StationStatistics.objects.get(station=project, year_month=year_month)
            mdfs = MonthlyDistributionForm.objects.filter(
                Q(month_year__month=the_mdf.month_year.month) &
                Q(month_year__year=the_mdf.month_year.year) &
                (Q(requests__project=project) | Q(mdfitem_set__project=project)))
            
            total_budget = 0
            for mdf in mdfs:
                total_budget += mdf.station_total(project)
            stats.budget = total_budget
            stats.save()
            
                
                
class MdfItemViewSet(viewsets.ModelViewSet):
    queryset = MdfItem.objects.all()
    serializer_class = MdfItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ['description']
    ordering_fields = ['category', 'description', 'work_project']
    ordering = ['work_project']
        
        
        