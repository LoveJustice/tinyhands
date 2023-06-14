from rest_framework import serializers
from budget.models import BorderStationBudgetCalculation, OtherBudgetItemCost, StaffBudgetItem
from budget.models import MonthlyDistributionMultipliers, ProjectRequest, ProjectRequestDiscussion, ProjectRequestAttachment, ProjectRequestComment
from dataentry.serializers import BorderStationSerializer
from static_border_stations.models import Staff
from budget.mdf_constants import REQUEST_CATEGORY_CHOICES_MDF


class BorderStationBudgetCalculationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BorderStationBudgetCalculation
        fields = [
            'id',
            'mdf_uuid',
            'border_station',
            'month_year',
            'date_time_entered',
            'date_time_last_updated',
            'date_finalized',
        ]

    border_station = BorderStationSerializer(read_only=True)


class BorderStationBudgetCalculationSerializer(serializers.ModelSerializer):
    def validate(self, data):
        borderstation = data["border_station"]
        monthyear = data["month_year"]

        if BorderStationBudgetCalculation.objects.filter(border_station=borderstation, month_year__month=monthyear.month, month_year__year=monthyear.year).count() > 0 and not self.instance:
            raise serializers.ValidationError('A budget has already been created for this month!')
        return data


    class Meta:
        fields = '__all__'
        model = BorderStationBudgetCalculation

    default = True


class OtherBudgetItemCostSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = OtherBudgetItemCost
        

class StaffBudgetItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffBudgetItem
        fields = [field.name for field in model._meta.fields] # all the model fields
        fields = fields + ['staff_first_name','staff_last_name','position']
    
    staff_first_name = serializers.SerializerMethodField(read_only=True)
    staff_last_name = serializers.SerializerMethodField(read_only=True)
    position = serializers.SerializerMethodField(read_only=True)
    
    def get_staff_first_name(self, obj):
        return obj.staff_person.first_name
    def get_staff_last_name(self, obj):
        return obj.staff_person.last_name
    def get_position(self, obj):
        return obj.staff_person.position
    
class ProjectRequestDiscussionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectRequestDiscussion
        fields = [field.name for field in model._meta.fields] # all the model fields
        fields = fields + ['author_email', 'notify_emails']
    
    author_email = serializers.SerializerMethodField(read_only=True)
    notify_emails = serializers.SerializerMethodField(read_only=True)
    
    def get_author_email(self, obj):
        if obj.author is None:
            return ''
        else:
            return obj.author.email
    
    def get_notify_emails(self, obj):
        emails = ''
        sep = ''
        for account in obj.notify.all():
            emails += sep + account.email
            sep = ','
        
        return emails
            
        
class ProjectRequestAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectRequestAttachment
        fields = [field.name for field in model._meta.fields] # all the model fields

class ProjectRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectRequest
        fields = [field.name for field in model._meta.fields] # all the model fields
        fields = fields + ['country_id', 'projectrequestdiscussion_set', 'projectrequestattachment_set', 'author_email',
                           'project_name','category_name', 'approved_mdf', 'pending_mdf', 'staff_name', 'default_mdf_project_id',
                           'drop_decimal', 'first_mdf_id', 'comment_list']
    
    projectrequestdiscussion_set = ProjectRequestDiscussionSerializer(many=True, read_only=True)
    projectrequestattachment_set = ProjectRequestAttachmentSerializer(many=True, read_only=True)
    country_id = serializers.SerializerMethodField(read_only=True)
    author_email = serializers.SerializerMethodField(read_only=True)
    project_name = serializers.SerializerMethodField(read_only=True)
    category_name = serializers.SerializerMethodField(read_only=True)
    approved_mdf = serializers.SerializerMethodField(read_only=True)
    pending_mdf = serializers.SerializerMethodField(read_only=True)
    staff_name = serializers.SerializerMethodField(read_only=True)
    default_mdf_project_id = serializers.SerializerMethodField(read_only=True)
    drop_decimal = serializers.SerializerMethodField(read_only=True)
    first_mdf_id = serializers.SerializerMethodField(read_only=True)
    comment_list = serializers.SerializerMethodField(read_only=True)
    
    def get_country_id(self, obj):
        return obj.project.operating_country.id
    
    def get_author_email(self, obj):
        if obj.author is None:
            return ''
        else:
            return obj.author.email
    
    def get_project_name(self, obj):
        return obj.project.station_name
    
    def get_category_name(self, obj):
        name = ''
        for category in REQUEST_CATEGORY_CHOICES_MDF:
            if obj.category == category[0]:
                name = category[1]
                break
        
        return name
    
    def get_approved_mdf(self, obj):
        found = False
        if obj.prior_request is not None:
            found = True
        else:
            qs = obj.monthlydistributionform_set.filter(status='Approved')
            if len(qs) > 0:
                found = True
        return found
    
    def get_pending_mdf(self, obj):
        found = False
        qs = obj.monthlydistributionform_set.all().exclude(status='Approved')
        if len(qs) > 0:
            found = True
        return found
    
    def get_staff_name(self, obj):
        staff_name = ''
        if obj.staff is not None:
            staff_name = obj.staff.first_name + ' ' + obj.staff.last_name
        return staff_name
    
    def get_default_mdf_project_id(self, obj):
        rv = obj.project.id
        if obj.project.mdf_project is not None:
            rv = obj.project.mdf_project.id
        
        return rv
    
    def get_drop_decimal(self, obj):
        drop_decimal = False
        country =  obj.project.operating_country
        if 'drop_decimal' in country.options:
            drop_decimal = country.options['drop_decimal']
        return drop_decimal
    
    def get_first_mdf_id(self, obj):
        first_id = None
        mdfs = obj.monthlydistributionform_set.all().order_by('month_year')
        if len(mdfs) > 0:
            first_id = mdfs[0].id
        
        return first_id
    
    def get_comment_list(self, obj):
        comment_list = []
        comments = ProjectRequestComment.objects.filter(request=obj)
        for comment in comments:
            comment_list.append({'type':comment.type, 'comment':comment.comment})
        
        return comment_list
        
        
class MonthlyDistributionMultipliersSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyDistributionMultipliers
        fields = [field.name for field in model._meta.fields] # all the model fields

class ProjectRequestAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectRequestAttachment
        fields = [field.name for field in model._meta.fields] # all the model fields
    
        
        