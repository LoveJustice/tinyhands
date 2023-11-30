import datetime
from decimal import Decimal
from rest_framework import serializers
from django.conf import settings
from budget.models import ProjectRequest
import budget.mdf_constants as constants
from dataentry.models import BorderStation, CountryExchange
from static_border_stations.models import Staff, StaffProject, StaffReview, CommitteeMember, Location, WorksOnProject

class StaffProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffProject
        fields = [field.name for field in model._meta.fields] # all the model fields
        fields = fields + ['project_code']
        
    project_code = serializers.SerializerMethodField(read_only=True)
    
    def get_project_code (self, obj):
        return obj.border_station.station_code

class SttaffReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffReview
        fields = [field.name for field in model._meta.fields] # all the model fields

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'position',
                  'receives_money_distribution_form', 'border_station', 'country',
                  'first_date', 'last_date', 'birth_date', 'total_years',
                  'education', 'id_card', 'works_on', 'staffproject_set',
                  'contract_data', 'knowledge_data', 'review_data']
    
    total_years = serializers.SerializerMethodField(read_only=True)
    works_on = serializers.SerializerMethodField(read_only=True)
    staffproject_set = StaffProjectSerializer(many=True)
    contract_data = serializers.SerializerMethodField(read_only=True)
    knowledge_data = serializers.SerializerMethodField(read_only=True)
    review_data = serializers.SerializerMethodField(read_only=True)
    
    def view_section(self, obj, data_type):
        result = False
        if 'request' in self.context:
            request = self.context['request']
        else:
            request = None
        if request is None:
            request_types = ''
        else:
            request_types = request.GET.get('include')
            if request_types is None:
                request_types = ''
        if request_types is not None and data_type in request_types:
            result = True
            
        return result
    
    def has_permission(self, request):
        return True
    
    def file_value(self, instance):
        result = ''
        if instance is not None and instance.name != '':
            result = settings.MEDIA_URL + instance.name
        
        return result
    
    def get_total_years(self, obj):
        if obj.first_date is not None:
            delta = datetime.datetime.today().date() - obj.first_date
            years = delta.days/356
        else:
            years = None
        return years
    
    def get_works_on (self, obj):
        rtn = []
        works_on_list = WorksOnProject.objects.filter(staff=obj)
        for works_on in works_on_list:
            rtn.append({
                'id': works_on.id,
                'financial': {
                    'project_id': obj.border_station.id,
                    'project_name': obj.border_station.station_name,
                    'project_code': obj.border_station.station_code
                },
                'works_on':{
                    'project_id': works_on.border_station.id,
                    'project_name': works_on.border_station.station_name,
                    'project_code': works_on.border_station.station_code
                },
                'percent':works_on.work_percent})
        return rtn
    
    def get_contract_month_sum(self, requests, year_month):
        result = {
                "local":0,
                "usd":0
            }
        
        if len(requests) > 0:
            exchanges = CountryExchange.objects.filter(country=requests[0].project.operating_country, year_month__lte=year_month).order_by('-year_month')
            exchange_rate = Decimal(exchanges[0].exchange_rate)
        else:
            exchange_rate = Decimal(1.0)
            
        for project_request in requests:
            if not self.has_permission(project_request):
                continue
            if project_request.benefit_type_name == 'deduct':
                result['local'] -= project_request.cost
            else:
                result['local'] += project_request.cost
        
        result['usd'] = result['local'] * exchange_rate
            
            
        return result
    
    def get_contract_data(self, obj):
        if  not self.view_section(obj, 'VIEW_CONTRACT'):
            return None
        
        today = datetime.datetime.today()
        month = today.month
        year = today.year
        
        if month == 1:
            month = 12
            year -= 1
        else:
            month -= 1
        
        last_month_local = 0
        last_month_usd = 0
        year_total_local = 0
        year_total_usd = 0
        
        requests = ProjectRequest.objects.filter(
                staff = obj,
                category=constants.STAFF_BENEFITS,
                monthlydistributionform__month_year__month=month,
                monthlydistributionform__month_year__year=year,
            )
        result = self.get_contract_month_sum(requests, year*100 + month)
        last_month_local = result['local']
        last_month_usd = result['usd']
        year_total_local = result['local']
        year_total_usd = result['usd']
        
        for months in range(0,11):
            if month == 1:
                month = 12
                year -= 1
            else:
                month -= 1
            requests = ProjectRequest.objects.filter(
                    staff = obj,
                    category=constants.STAFF_BENEFITS,
                    monthlydistributionform__month_year__month=month,
                    monthlydistributionform__month_year__year=year,
                )
            result = self.get_contract_month_sum(requests, year*100 + month)
            year_total_local += result['local']
            year_total_usd += result['usd']         
        
        result = {
                "agreement":self.file_value(obj.agreement),
                "contract":self.file_value(obj.contract),
                "contract_expiration":self.file_value(obj.contract_expiration),
                "last_month":{"local":last_month_local, "USD": last_month_usd},
                "twelve_month":{"local":year_total_local, "USD": year_total_usd}
            }
        return result
    
    def get_knowledge_data(self, obj):
        if  not self.view_section(obj, 'VIEW_KNOWLEDGE'):
            return None
        result = {
            "general":obj.general,
            "awareness":obj.awareness,
            "security":obj.security,
            "accounting":obj.accounting,
            "pv_care":obj.pv_care,
            "paralegal":obj.paralegal,
            "records":obj.records
            }
        return result
    
    def get_review_data(self, obj):
        if  not self.view_section(obj, 'VIEW_REVIEW'):
            return None
        reviews = StaffReview.objects.filter(staff=obj).order_by('-review_date')
        if len(reviews) > 0 :
            reviewSerializer=StaffReviewSerializer(reviews[0])
            return [reviewSerializer.data]
        return []
    
    def to_internal_value(self, data):
        if 'staffproject_set' in data:
            staff_project = data['staffproject_set']
            data['staffproject_set'] = []
        else:
            data['staffproject_set'] = []
            staff_project = []
        validated = super().to_internal_value(data)
        validated['staffproject_set'] = staff_project
        return validated
    
    def update(self, instance, validated_data):
        staff_project = validated_data['staffproject_set']
        del validated_data['staffproject_set']
        obj = super().update(instance, validated_data)
        to_delete = []
        staff_project_list = StaffProject.objects.filter(staff=obj)
        for existing in staff_project_list:
            found = False
            for new_data in staff_project:
                if existing.id == new_data['id']:
                    found = True
                    existing.receives_money_distribution_form = new_data['receives_money_distribution_form']
                    existing.coordinator = new_data['coordinator']
                    existing.save()
                    break
            if not found:
                to_delete.append(existing)

        for existing in to_delete:
            existing.delete()

        for new_data in staff_project:
            if new_data['id'] is None:
                entry = StaffProject()
                entry.staff = instance
                entry.border_station = BorderStation.objects.get(id=new_data['border_station'])
                entry.receives_money_distribution_form = new_data['receives_money_distribution_form']
                entry.coordinator = new_data['coordinator']
                entry.save()
        
        return obj

    def create(self, validated_data):
        staff_project = validated_data['staffproject_set']
        del validated_data['staffproject_set']
        obj = super().create(validated_data)
        obj.save()
        for new_data in staff_project:
            entry = StaffProject()
            entry.staff = obj
            entry.border_station = BorderStation.objects.get(id=new_data['border_station'])
            entry.receives_money_distribution_form = new_data['receives_money_distribution_form']
            entry.coordinator = new_data['coordinator']
            entry.save()
        
        return obj



class CommitteeMemberSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = CommitteeMember


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Location
