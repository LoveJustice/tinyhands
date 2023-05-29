from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_api.authentication_expansion import HasPermission, HasDeletePermission, HasPostPermission, HasPutPermission
from rest_framework import filters as fs
from rest_framework.response import Response

import budget.mdf_constants as constants
from budget.serializers import MonthlyDistributionMultipliersSerializer, ProjectRequestSerializer, ProjectRequestDiscussionSerializer
from budget.models import MonthlyDistributionForm, MonthlyDistributionMultipliers, ProjectRequest, ProjectRequestDiscussion
from dataentry.models import BorderStation, Permission, UserLocationPermission
from accounts.serializers import AccountsSerializer

class ProjectRequestViewSet(viewsets.ModelViewSet):
    queryset = ProjectRequest.objects.all()
    serializer_class = ProjectRequestSerializer
    permission_classes = [IsAuthenticated, HasPermission, HasDeletePermission, HasPostPermission, HasPutPermission]
    permissions_required = [{'permission_group':'PROJECT_REQUEST', 'action':'VIEW'},]
    delete_permissions_required = [{'permission_group':'PROJECT_REQUEST', 'action':'DELETE'},]
    post_permissions_required = [{'permission_group':'PROJECT_REQUEST', 'action':'ADD'},]
    put_permissions_required = [{'permission_group':'PROJECT_REQUEST', 'action':'ADD'},]
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ['project__station_name', 'status', 'description']
    ordering_fields = ['project__station_name', 'status', 'date_time_entered']
    ordering = ('-date_time_entered',)
    
    def get_queryset(self):
        border_stations = UserLocationPermission.get_stations_with_permission(self.request.user.id, 'PROJECT_REQUEST','VIEW')
        border_station_ids = []
        for border_station in border_stations:
            border_station_ids.append(border_station.id)
        queryset = ProjectRequest.objects.filter(project__id__in=border_station_ids)
        project_id = self.request.GET.get('project_id')
        if project_id is not None and project_id != '':
            queryset = queryset.filter(project__id=project_id)
        else:
            in_country = self.request.GET.get('country_ids')
            if in_country is not None and in_country != '':
                queryset = queryset.filter(project__operating_country__id__in=in_country.split(','))
        status = self.request.GET.get('status')
        if status is not None and status != '':
            queryset = queryset.filter(status=status)
        frequency = self.request.GET.get('frequency')
        if frequency is not None and frequency != '':
            if frequency == 'monthly':
                queryset = queryset.filter(monthly=True)
            elif frequency == 'single':
                queryset = queryset.filter(monthly=False)

        return queryset
    
    def update(self, request, pk):
        current = ProjectRequest.objects.get(id=pk)
        current_status = current.status
        if UserLocationPermission.has_session_permission(request, 'MDF', 'REVIEW1', current.project.id, current.project.operating_country.id):
            has_review = True
            has_approve = True
            is_author = False
        elif UserLocationPermission.has_session_permission(request, 'PROJECT_REQUEST', 'APPROVE', current.project.id, current.project.operating_country.id):
            has_review = False
            has_approve = True
            is_author = False
        elif current.author == request.user:
            is_author = True
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        serializer =  ProjectRequestSerializer(current, request.data)
        if serializer.is_valid():
            project_request = serializer.save()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
            
        mdf_list = MonthlyDistributionForm.objects.filter(project=project_request.project).exclude(status='Approved')
        if is_author and project_request.status != 'Submitted':
            project_request.status = 'Submitted'
            project_request.save()
            if len(mdf_list) > 0:
                try:
                    mdf_list[0].requests.remove(project_request)
                except:
                    pass
        elif not has_review:
            if len(mdf_list) > 0:
                mdf_list[0].status = 'Submitted'
                mdf_list[0].save()
        
        serializer =  ProjectRequestSerializer(project_request)
        return Response(serializer.data)
    
    def get_category_types(self, request, project_id):
        response = []
        station = BorderStation.objects.get(id=project_id)
        if 'hasMDF' in station.features:
            categories = constants.REQUEST_CATEGORY_CHOICES_MDF
        else:
            categories = constants.REQUEST_CATEGORY_CHOICES_NO_MDF
        for category in categories:
            response.append({"id": category[0], "text": category[1]})
        
        return Response(response)
    
    def get_benefit_types(self, request, project_id):
        benefits = ProjectRequest.objects.filter(project__id=project_id, category=constants.STAFF_BENEFITS).order_by('benefit_type_name').values('benefit_type_name').distinct()
        response = []
        for benefit in benefits:
            response.append(benefit['benefit_type_name'])
        if 'Deductions' not in response:
            response.append('Deductions')
        if 'Salary' not in response:
            response.append('Salary')
        response.sort()
            
        
        return Response(response)
    
    def get_multipliers(self, request):
        multipliers = MonthlyDistributionMultipliers.objects.all().order_by('name')
        serializer = MonthlyDistributionMultipliersSerializer(multipliers, many=True)
        return Response(serializer.data)
    
    def approve(self, request, pk):
        project_request = ProjectRequest.objects.get(id=pk)
        if project_request.status != 'Submitted':
            Response(status=status.HTTP_400_BAD_REQUEST)
        project_request.status = 'Approved'
        project_request.save()
        
        mdf_list = MonthlyDistributionForm.objects.filter(project=project_request.project).exclude(status='Approved')
        if len(mdf_list) > 0:
            mdf_list[0].requests.add(project_request)
        
        serializer = ProjectRequestSerializer(project_request)
        
        return Response(serializer.data)
        
    
class ProjectRequestDiscussionViewSet(viewsets.ModelViewSet):
    queryset = ProjectRequestDiscussion.objects.all()
    serializer_class = ProjectRequestDiscussionSerializer
    permission_classes = [IsAuthenticated, HasPermission, HasDeletePermission, HasPostPermission, HasPutPermission]
    permissions_required = [{'permission_group':'PROJECT_REQUEST', 'action':'VIEW'},]
    delete_permissions_required = [{'permission_group':'PROJECT_REQUEST', 'action':'DELETE'},]
    post_permissions_required = [{'permission_group':'PROJECT_REQUEST', 'action':'VIEW'},]
    put_permissions_required = [{'permission_group':'PROJECT_REQUEST', 'action':'EDIT'},]
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = []
    ordering_fields = ['date_time_entered']
    ordering = ('-date_time_entered',)
    
    
    def get_queryset(self):
        qs = self.queryset
        request_id = self.request.GET.get('request_id')
        if request_id is not None and request_id != '':
            qs = qs.filter(request__id=request_id)

        return qs
    
    def get_notify_accounts(self, request, id):
        project_request = ProjectRequest.objects.get(id=id)
        permission = Permission.objects.get(permission_group='PROJECT_REQUEST', action='VIEW')
        ulps = UserLocationPermission.objects.filter(permission=permission, country__isnull=True, station__isnull=True)
        ulps2 = UserLocationPermission.objects.filter(permission=permission, country=project_request.project.operating_country.id, station__isnull=True)
        ulps3 = UserLocationPermission.objects.filter(permission=permission,station=project_request.project.id)
        ulps_all = (ulps | ulps2 | ulps3).order_by('account__email')
        account_list = []
        for ulp in ulps_all:
            account_list.append(ulp.account)
        
        serializer = AccountsSerializer(account_list, many=True)
        return Response(serializer.data)
       
            
    