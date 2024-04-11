import datetime
from dateutil.relativedelta import relativedelta
import json
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_api.authentication_expansion import HasPermission, HasDeletePermission, HasPostPermission, HasPutPermission
from rest_framework import filters as fs
from rest_framework.response import Response
from django.db.models import Q
from django.core.files.storage import default_storage
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
from templated_email import send_templated_mail

from accounts.models import Account
import budget.mdf_constants as constants
from budget.serializers import MonthlyDistributionMultipliersSerializer, ProjectRequestSerializer, ProjectRequestAttachmentSerializer, ProjectRequestDiscussionSerializer
from budget.models import MonthlyDistributionForm, MonthlyDistributionMultipliers, ProjectRequest, ProjectRequestAttachment, ProjectRequestDiscussion, ProjectRequestComment
from dataentry.models import BorderStation, Permission, UserLocationPermission
from accounts.serializers import AccountsSerializer

class ProjectRequestViewSet(viewsets.ModelViewSet):
    queryset = ProjectRequest.objects.all()
    serializer_class = ProjectRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ['project__station_name', 'status', 'description']
    ordering_fields = ['project__station_name', 'status', 'date_time_entered']
    ordering = ('-date_time_entered',)
    
    def get_queryset(self):
        mdf_id = self.request.GET.get('mdf_id')
        if mdf_id is not None and mdf_id != '':
            mdf = MonthlyDistributionForm.objects.get(id=mdf_id)
            return mdf.requests.filter(discussion_status='Open')
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
        category = self.request.GET.get('category')
        if category is not None and category != '':
            queryset = queryset.filter(category=category)
        status = self.request.GET.get('status')
        if status is not None and status != '':
            queryset = queryset.filter(status=status)
        frequency = self.request.GET.get('frequency')
        if frequency is not None and frequency != '':
            if frequency == 'monthly':
                queryset = queryset.filter(monthly=True)
            elif frequency == 'single':
                queryset = queryset.filter(monthly=False)
        discussion = self.request.GET.get('discussion')
        if discussion == 'Open':
            queryset = queryset.filter(discussion_status='Open')
        elif discussion == 'Includes Me':
            my_discussions = set(ProjectRequestDiscussion.objects.filter(Q(author=self.request.user.id) | Q(notify=self.request.user)).values_list('request__id', flat=True))
            queryset = queryset.filter(id__in=my_discussions)
        elif discussion == 'Waiting on Me':
            my_discussions = set(ProjectRequestDiscussion.objects.filter(notify=self.request.user,
                    request__discussion_status='Open').exclude(response=self.request.user).values_list('request__id', flat=True))
            queryset = queryset.filter(id__in=my_discussions)
            
        queryset = queryset.exclude(category=constants.MULTIPLIERS)

        return queryset
    
    def create(self, request):
        project_id = request.data['project']
        project = BorderStation.objects.get(id=project_id)
        if not UserLocationPermission.has_session_permission(request, 'PROJECT_REQUEST', 'ADD', project.operating_country.id,  project.id):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        return super().create(request)
    
    def update(self, request, pk):
        current = ProjectRequest.objects.get(id=pk)
        current_status = current.status
        current_cost = current.cost
        comment_request = current
        if not UserLocationPermission.has_session_permission(request, 'PROJECT_REQUEST', 'ADD', current.project.operating_country.id, current.project.id):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        if UserLocationPermission.has_session_permission(request, 'MDF', 'INITIAL_REVIEW', current.project.operating_country.id, current.project.id):
            has_review = True
            has_approve = True
            is_author = False
        elif UserLocationPermission.has_session_permission(request, 'PROJECT_REQUEST', 'APPROVE', current.project.operating_country.id, current.project.id):
            has_review = True
            has_approve = True
            is_author = False
        elif current.author == request.user:
            has_review = False
            has_approve = False
            is_author = True
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        mdf_list = MonthlyDistributionForm.objects.filter(status='Approved', requests=current).order_by('-month_year')
        on_approved_mdf = (len(mdf_list) > 0)
        update_type = None
        comment = None
        if 'comment' in request.data and request.data['comment'] != '':
            comment = request.data['comment']
        
        override_mdf = current.override_mdf_project
        if request.data['override_mdf_project'] != str(override_mdf.id):
            current.monthlydistributionform_set.clear()
            override_mdf = None
            if request.data['override_mdf_project'] is not None:
                override_mdf = BorderStation.objects.get(id=request.data['override_mdf_project'])
        
        # should be at most one non-approved MDF for the project
        pending_mdf_list = MonthlyDistributionForm.objects.filter(border_station=override_mdf).exclude(status='Approved')
        
        if on_approved_mdf:
            # Either the amount is being changed or the request is completed
            if current.status != 'Approved':
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            current.status = 'Approved-Completed'
            current.completed_date_time = mdf_list[0].month_year + relativedelta(days=1)
        
            if request.data['status'] != 'Declined':
                if pending_mdf_list.exists():
                    pending_mdf_list[0].requests.remove(current)
                else:
                    pass
                project_request = ProjectRequest.objects.get(id=pk)
                project_request.id = None
                if 'cost' not in request.data:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
                
                project_request.cost = request.data['cost']
                update_type = 'Change Amount'
                project_request.prior_request = current
                project_request.save()
                
                comment_request = project_request
                
                if not has_review:
                    if len(pending_mdf_list) > 0:
                        pending_mdf_list[0].status = 'Submitted'
                        pending_mdf_list[0].save()
                if project_request.status == 'Approved' and len(pending_mdf_list) > 0:
                    try:
                         pending_mdf_list[0].requests.add(project_request)
                    except IntegrityError:
                        pass
            else:
                # should never occur
                project_request = current
                update_type = 'Completed'
            
            current.save()
        elif current.prior_request:
            project_request = current
            if request.data['status'] != 'Declined':
                project_request.cost = request.data['cost']
                update_type = 'Change Amount'
            else:
                update_type = 'Completed'
                project_request.status = 'Approved-Completed'
                project_request.completed_date_time = project_request.prior_request.completed_date_time
            project_request.save()
        else:
            # Not on approved MDF
            serializer =  ProjectRequestSerializer(current, request.data)
            if serializer.is_valid():
                project_request = serializer.save()
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            if is_author:
                project_request.cost = project_request.original_cost
                if project_request.status != 'Submitted':
                     project_request.status = 'Submitted'
                project_request.save()
            
            if len(pending_mdf_list) > 0:
                if project_request.status == 'Submitted':
                    try:
                        pending_mdf_list[0].requests.remove(project_request)
                    except ObjectDoesNotExist:
                        pass
                else:
                    try:
                        pending_mdf_list[0].requests.add(project_request)
                    except IntegrityError:
                        pass
            
            if project_request.status == 'Declined':
                update_type = 'Declined'
            elif current_cost != project_request.cost:
                update_type = 'Change Amount'
        
        if comment is not None and update_type is not None:
            comment = request.data['comment']
            if comment is not None and comment != '':
                # We only want one comment for a project request per MDF.  So we will update
                # any existing comment that has not yet appeared on an approved MDF.
                try:
                    # existing comment that has not been assigned to an MDF yet
                    current_comment = ProjectRequestComment.objects.get(request=comment_request, mdf__isnull=True)
                except ObjectDoesNotExist:
                    try:
                        # existing comment that has been assigned to an MDF that is not yet approved
                        current_comment = ProjectRequestComment.objects.get(request=comment_request).exclude(mdf__status='Approved')
                    except ObjectDoesNotExist:
                        current_comment = ProjectRequestComment()
                        current_comment.request = comment_request
                current_comment.type = update_type
                current_comment.comment = comment
                current_comment.save() 
        
        serializer =  ProjectRequestSerializer(project_request)
        return Response(serializer.data)
    
    # Change the discussion status without the additional logic of the normal update
    def update_discussion_status (self, request, pk):
        project_request = ProjectRequest.objects.get(id=pk)
        project_request.discussion_status = request.data['discussion_status']
        project_request.save()
        
        discussion = ProjectRequestDiscussion()
        discussion.request = project_request
        discussion.author = self.request.user
        if project_request.discussion_status == 'Open':
            discussion.text = 'Open Discussion'
        else:
            discussion.text = 'Close Discussion'
        discussion.save()
        
        serializer =  ProjectRequestDiscussionSerializer(discussion)
        return Response(serializer.data)
    
    def get_category_types(self, request, project_id):
        response = []
        if int(project_id) >= 0:
            station = BorderStation.objects.get(id=project_id)
        
        if int(project_id) < 0 or 'hasMDF' in station.features:
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
    
class ProjectRequestDiscussionViewSet(viewsets.ModelViewSet):
    queryset = ProjectRequestDiscussion.objects.all()
    serializer_class = ProjectRequestDiscussionSerializer
    permission_classes = [IsAuthenticated, HasPermission, HasDeletePermission, HasPostPermission, HasPutPermission]
    permissions_required = [{'permission_group':'PROJECT_REQUEST', 'action':'VIEW'},]
    delete_permissions_required = [{'permission_group':'PROJECT_REQUEST', 'action':'DELETE'},]
    post_permissions_required = [{'permission_group':'PROJECT_REQUEST', 'action':'VIEW'},]
    put_permissions_required = [{'permission_group':'PROJECT_REQUEST', 'action':'VIEW'},]
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
    
    def create(self, request):
        serializer = ProjectRequestDiscussionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        discussion = serializer.save()
        
        category_name = ''
        for category in constants.CATEGORY_CHOICES:
            if category[0] == discussion.request.category:
                category_name = category[1]
                
        for account_id in request.data['notify']:
            account = Account.objects.get(id=account_id)
            discussion.notify.add(account)
        
            context = {}
            context['staff'] = account.get_full_name()
            context['Comment_user'] = request.user.get_full_name()
            context['url'] = settings.CLIENT_DOMAIN +'/reviewProjectRequests?id=' + str(discussion.request.id)
            context['Project'] = discussion.request.project.station_name
            context['Category'] = category_name
            context['Description'] = discussion.request.description
            context['Comment'] = discussion.text
            send_templated_mail(
                template_name='discussion_notify',
                from_email=settings.ADMIN_EMAIL_SENDER,
                recipient_list=[account.email],
                context=context
            )
        
        open_notify = ProjectRequestDiscussion.objects.filter(request=discussion.request, request__discussion_status='Open', 
                        notify=discussion.author).exclude(id=discussion.id).exclude(response=discussion.author)
        for entry in open_notify:
            try:
                entry.response.add(discussion.author)
            except IntegrityError:
                pass
        
        serializer = ProjectRequestDiscussionSerializer(discussion)
        return Response(serializer.data)
    
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
       
class ProjectRequestAttachmentViewSet(viewsets.ModelViewSet):
    queryset = ProjectRequestAttachment.objects.all() 
    serializer_class = ProjectRequestAttachmentSerializer
    permission_classes = [IsAuthenticated, HasPermission, HasDeletePermission, HasPostPermission, HasPutPermission]
    permissions_required = [{'permission_group':'PROJECT_REQUEST', 'action':'VIEW'},]
    delete_permissions_required = [{'permission_group':'PROJECT_REQUEST', 'action':'VIEW'},]
    post_permissions_required = [{'permission_group':'PROJECT_REQUEST', 'action':'VIEW'},]
    put_permissions_required = [{'permission_group':'PROJECT_REQUEST', 'action':'VIEW'},] 
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    ordering_fields = ['id']
    ordering = ('-id',)
    
    def get_queryset(self):
        queryset = ProjectRequestAttachment.objects.all() 
        request_id = self.request.GET.get('request_id')
        if request_id is not None and request_id != '':
            queryset = queryset.filter(request__id=request_id)
        
        return queryset;
    
    def create(self, request):
        if 'main' in request.data:
            request_string = request.data['main']
            request_json = json.loads(request_string)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        if 'scanned' in request.data:
            file_obj = request.data['scanned']
            request_json['attachment'] = file_obj
        
        serializer = ProjectRequestAttachmentSerializer(data=request_json)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        attachment = serializer.save()
        
        serializer = ProjectRequestAttachmentSerializer(attachment)
        return Response(serializer.data)
    