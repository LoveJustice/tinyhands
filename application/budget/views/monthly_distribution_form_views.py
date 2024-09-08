import datetime
from dateutil.relativedelta import relativedelta
from rest_framework import viewsets, status
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters as fs
from rest_framework.response import Response
from django.apps import apps
from django.db.models import Value, IntegerField, Q
from django.contrib.contenttypes.models import ContentType

from dataentry.models import BorderStation, IntercepteeCommon, StationStatistics, UserLocationPermission
from dataentry.serializers import CountrySerializer
from budget.models import BorderStationBudgetCalculation, MonthlyDistributionForm, MdfCombined, MdfItem, ProjectRequest, ProjectRequestComment, ProjectRequestDiscussion
from budget.serializers import MonthlyDistributionFormSerializer, MdfItemSerializer
from export_import.mdf_io import export_mdf_sheet
from mailbox import MMDF

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
        status = self.request.GET.get('status')
        if status is not None and status != '':
            queryset = queryset.filter(status=status)
        
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
    
    def get_last_mdf_date(self, request, station_id):
        mdfs = MonthlyDistributionForm.objects.filter(border_station__id=station_id).order_by('-month_year')
        if len(mdfs) > 0:
            year_month = mdfs[0].month_year.year * 100 + mdfs[0].month_year.month
            rv = {'month':year_month, 'status':mdfs[0].status}
        else:
            rv = {'month':None, 'status':None}
        
        return Response(rv)
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
        mdf.status = 'Pending'
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
            
        if not ((mdf.status == 'Pending' and UserLocationPermission.has_session_permission(request, 'MDF', 'ADD', mdf.border_station.operating_country.id, mdf.border_station.id)) or
             (mdf.status == 'Submitted' and UserLocationPermission.has_session_permission(request, 'MDF', 'INITIAL_REVIEW', mdf.border_station.operating_country.id, mdf.border_station.id)) or
             (mdf.status == 'Initial Review' and UserLocationPermission.has_session_permission(request, 'MDF', 'FINAL_REVIEW', mdf.border_station.operating_country.id, mdf.border_station.id))):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        if mdf.status == 'Pending':
            mdf.status = 'Submitted'
            mdf.save()
        else:
            # Close open discussions
            project_requests = mdf.requests.filter(discussion_status='Open')
            for project_request in project_requests:
                discussion = ProjectRequestDiscussion()
                discussion.request = project_request
                discussion.author = request.user
                discussion.text = 'Closed on MDF approval'
                discussion.save()
                project_request.discussion_status = 'Closed'
                project_request.save()
            
            if mdf.status == 'Submitted':
                mdf.status = 'Initial Review'
                mdf.save()
            else:
                completed_date_time = mdf.month_year + relativedelta(days=1)
                mdf.status = 'Approved'
                project_requests = mdf.requests.all()
                for project_request in project_requests:
                    if project_request.status == 'Declined':
                        project_request.status = 'Declined-Completed'
                        project_request.completed_date_time = completed_date_time
                        project_request.save()
                    elif project_request.status == 'Approved' and project_request.monthly == False:
                        project_request.status = 'Approved-Completed'
                        project_request.completed_date_time = completed_date_time
                        project_request.save()
                comments = ProjectRequestComment.objects.filter(mdf__isnull=True, request__in = mdf.requests.all())
                for comment in comments:
                    comment.mdf = mdf 
                    comment.save()
                mdf.save()
                staff_class = apps.get_model('static_border_stations', 'Staff')
                staff_class.set_mdf_totals(mdf)
                self.check_update_stats(mdf)
       
        serializer = self.serializer_class(mdf)
        return Response(serializer.data)
    
    def check_update_stats(self, mdf):
        open_mdf_projects = BorderStation.objects.filter(
                operating_country=mdf.border_station.operating_country,
                open=True,
                features__contains='hasMDF')
        approved_mdfs = MonthlyDistributionForm.objects.filter(
                status = 'Approved',
                border_station__in=open_mdf_projects,
                month_year__year = mdf.month_year.year,
                month_year__month = mdf.month_year.month)
        if len(approved_mdfs) < len(open_mdf_projects):
            # Not all of the MDFs for the country have been approved
            return False
        
        open_projects = BorderStation.objects.filter(
                operating_country=mdf.border_station.operating_country,
                open=True)
        
        year_month = mdf.month_year.year * 100 + mdf.month_year.month
        for project in open_projects:
            total_budget = 0
            for approved_mdf in approved_mdfs:
                total_budget += approved_mdf.full_total(project)
            
            try:
                stats = StationStatistics.objects.get(station=project, year_month=year_month)
            except:
                stats = StationStatistics()
                stats.station = project
                stats.year_month = year_month
            
            stats.budget = total_budget
            stats.save()
        
        export_mdf_sheet(mdf.border_station.operating_country, year_month)
        
        return True
    
    def retrieve_pdf(self, request, pk):
        mdf = MonthlyDistributionForm.objects.get(pk=pk)
        border_station = mdf.border_station
        staff = StaffProject.objects.filter(border_station=border_station).exclude(staff__email__isnull=True).value_list('staff', flat=True)
        committee_members = border_station.committeemember_set.exclude(email__isnull=True)
        
        # find all permissions for MDF Notification for the specified border station
        can_receive_mdf = UserLocationPermission.objects.filter(
            Q(permission__permission_group = 'NOTIFICATIONS') & Q(permission__action = 'MDF') &
            (Q(country = None) & Q(station=None) | Q(country__id = border_station.operating_country.id) | Q(station__id = border_station.id)))
        # add outer reference to account for the located permissions
        can_receive_mdf = can_receive_mdf.filter(account=OuterRef('pk'))
        # annotate the accounts that have permissions for receiving the MDF
        account_annotated = Account.objects.annotate(national_staff = Exists(can_receive_mdf))
        # select the annotated accounts
        national_staff = account_annotated.filter(national_staff=True)

        staff_serializer = StaffSerializer(staff, many=True)
        committee_members_serializer = CommitteeMemberSerializer(committee_members, many=True)
        national_staff_serializer = AccountMDFSerializer(national_staff, many=True)

        pdf_url = settings.SITE_DOMAIN + reverse('MdfPdf', kwargs={"uuid": budget.mdf_uuid})

        return Response({"staff_members": staff_serializer.data, "committee_members": committee_members_serializer.data, "national_staff_members": national_staff_serializer.data, "pdf_url": pdf_url})
            
                
                
class MdfItemViewSet(viewsets.ModelViewSet):
    queryset = MdfItem.objects.all()
    serializer_class = MdfItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ['description']
    ordering_fields = ['category', 'description', 'work_project']
    ordering = ['work_project']
        
        
        