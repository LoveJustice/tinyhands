from rest_framework import serializers
from budget.models import BorderStationBudgetCalculation, OtherBudgetItemCost, StaffSalary
from dataentry.serializers import BorderStationSerializer


class BorderStationBudgetCalculationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BorderStationBudgetCalculation
        fields = [
            'id',
            'border_station',
            'month_year',
            'date_time_entered',
            'date_time_last_updated',
        ]

    border_station = BorderStationSerializer(read_only=True)


class BorderStationBudgetCalculationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BorderStationBudgetCalculation

    default = True


class OtherBudgetItemCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherBudgetItemCost


class StaffSalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffSalary
