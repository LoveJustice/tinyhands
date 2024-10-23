from dateutil.relativedelta import relativedelta
from rest_framework import serializers
from django.core.files.storage import default_storage
from budget.models import BorderStationBudgetCalculation, OtherBudgetItemCost, StaffBudgetItem
from budget.models import MdfItem, ProjectRequest, ProjectRequestDiscussion, ProjectRequestAttachment, ProjectRequestComment
from budget.models import MonthlyDistributionForm, MonthlyDistributionMultipliers
from dataentry.models import BorderStation, CountryExchange
from dataentry.serializers import BorderStationSerializer
from static_border_stations.models import Staff
from static_border_stations.serializers import StaffSerializer
from budget.mdf_constants import REQUEST_CATEGORY_CHOICES_MDF
import budget.mdf_constants as constants
from django.conf import settings


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
            if comment.mdf is not None:
                mdf_id = comment.mdf.id
            else:
                mdf_id = None
            comment_list.append({'type':comment.type, 'comment':comment.comment, 'mdf':mdf_id})
        
        return comment_list
        
class MonthlyDistributionMultipliersSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyDistributionMultipliers
        fields = [field.name for field in model._meta.fields] # all the model fields

class ProjectRequestAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectRequestAttachment
        fields = [field.name for field in model._meta.fields] # all the model fields

class ProjectRequestCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectRequestComment
        fields = [field.name for field in model._meta.fields] # all the model fields
        
class MdfItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MdfItem
        fields = [field.name for field in model._meta.fields] # all the model fields
        
class MonthlyDistributionFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyDistributionForm
        fields = [field.name for field in model._meta.fields] # all the model fields
        fields = fields + ['station_name', 'requests', 'projectrequestcomment_set', 'mdfitem_set', 'related_projects', 'impact_projects',
                           'related_staff', 'country_id', 'country_currency', 'multiplier_types', 'drop_decimal', 'past_month_sent',
                           'exchange_rate', 'last_months_total', 'guide_progress']
    
    station_name = serializers.SerializerMethodField(read_only=True)   
    requests = ProjectRequestSerializer(many=True, read_only=True)
    projectrequestcomment_set = ProjectRequestCommentSerializer(many=True, read_only=True)
    mdfitem_set = MdfItemSerializer(many=True, read_only=True)
    related_projects = serializers.SerializerMethodField(read_only=True)
    impact_projects = serializers.SerializerMethodField(read_only=True)
    related_staff = serializers.SerializerMethodField(read_only=True)
    country_id = serializers.SerializerMethodField(read_only=True)
    country_currency = serializers.SerializerMethodField(read_only=True)
    multiplier_types = serializers.SerializerMethodField(read_only=True)
    drop_decimal = serializers.SerializerMethodField(read_only=True)
    past_month_sent = serializers.SerializerMethodField(read_only=True)
    exchange_rate = serializers.SerializerMethodField(read_only=True)
    last_months_total = serializers.SerializerMethodField(read_only=True)
    signed_pbs = serializers.SerializerMethodField(read_only=True)
    
    def get_station_name(self, obj):
        return obj.border_station.station_name
    
    def get_related_projects(self, obj):
        project_ids = ProjectRequest.objects.filter(monthlydistributionform=obj).values_list('project__id', flat=True)
        border_stations = BorderStation.objects.filter(id__in=project_ids)
        serializer = BorderStationSerializer(border_stations, many=True)
        return serializer.data
    
    def get_impact_projects(self, obj):
            impact_projects = BorderStation.objects.filter(mdf_project=obj.border_station)
            serializer = BorderStationSerializer(impact_projects, many=True)
            return serializer.data
    
    def get_related_staff(self, obj):
        staff_ids = ProjectRequest.objects.filter(monthlydistributionform=obj, staff__isnull=False).values_list('staff__id', flat=True)
        staff = Staff.objects.filter(id__in=staff_ids).order_by('first_name', 'last_name')
        serializer = StaffSerializer(staff, many=True)
        return serializer.data
        
    def get_country_id(self, obj):
        return obj.border_station.operating_country.id
    
    def get_country_currency(self, obj):
        return obj.border_station.operating_country.currency or ""
    
    def get_multiplier_types(self, obj):
        multipliers = MonthlyDistributionMultipliers.objects.all()
        serializer = MonthlyDistributionMultipliersSerializer(multipliers, many=True)
        return serializer.data
    
    def get_drop_decimal(self, obj):
        drop_decimal = False
        country =  obj.border_station.operating_country
        if 'drop_decimal' in country.options:
            drop_decimal = country.options['drop_decimal']
        return drop_decimal
    
    def get_past_month_sent(self, obj) :
        past_month_sent = False
        country =  obj.border_station.operating_country
        if 'pastMonthSent' in country.options and country.options['pastMonthSent']:
            past_month_sent = True
        
        return past_month_sent
    
    def get_exchange_rate(self, obj):
        rate = 1
        year_month = obj.month_year.year * 100 + obj.month_year.month
        exchange_list = CountryExchange.objects.filter(country=obj.border_station.operating_country, year_month__lte=year_month).order_by('-year_month')
        if len(exchange_list) > 0:
            rate = exchange_list[0].exchange_rate
        return rate
    
    def get_last_months_total(self, obj):
        result = None
        
        last_month_date = obj.month_year - relativedelta(months=1)
        mdfs = MonthlyDistributionForm.objects.filter(border_station=obj.border_station, month_year__year=last_month_date.year, month_year__month=last_month_date.month)
        if len(mdfs) > 0:
            result = str(mdfs[0].distribution_total(obj.border_station))
        else:
            budgets = BorderStationBudgetCalculation.objects.filter(border_station=obj.border_station, month_year__year=last_month_date.year, month_year__month=last_month_date.month)
            if len(budgets) > 0:
                result = str(budgets[0].station_total(obj.border_station) - budgets[0].money_not_spent_to_deduct_total(obj.border_station))
        
        return result
    
    def get_signed_pbs(self, obj):
        result = ''
        if obj.signed_pbs.name is not None and obj.signed_pbs.name != '':
            result  = settings.MEDIA_URL + obj.signed_pbs.name
        
        return result
    
    
        
        