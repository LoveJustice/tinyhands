from rest_framework import serializers
from budget.models import BorderStationBudgetCalculation, OtherBudgetItemCost, StaffSalary
from dataentry.serializers import BorderStationSerializer


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


class StaffSalarySerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = StaffSalary
