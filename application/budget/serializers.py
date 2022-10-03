from rest_framework import serializers
from budget.models import BorderStationBudgetCalculation, OtherBudgetItemCost, StaffBudgetItem
from dataentry.serializers import BorderStationSerializer
from static_border_stations.models import Staff


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
        
        