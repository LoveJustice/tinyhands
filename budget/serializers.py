from rest_framework import serializers
from budget.models import BorderStationBudgetCalculation, OtherBudgetItemCost, StaffSalary


class BorderStationBudgetCalculationSerializer(serializers.ModelSerializer):
    default = True

    class Meta:
        model = BorderStationBudgetCalculation


class OtherBudgetItemCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherBudgetItemCost


class StaffSalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffSalary

