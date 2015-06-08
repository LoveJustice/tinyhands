from rest_framework import serializers
from budget.models import BorderStationBudgetCalculation, OtherBudgetItemCost, StaffSalary


class BorderStationBudgetCalculationSerializer(serializers.ModelSerializer):
    # shelter_shelter_startup_amount = serializers.IntegerField(
    #     read_only=True,
    #     default=71800
    # )
    #
    # shelter_shelter_two_amount = serializers.IntegerField(
    #     read_only=True,
    #     default=36800
    # )

    default = True

    class Meta:
        model = BorderStationBudgetCalculation


class OtherBudgetItemCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherBudgetItemCost


class StaffSalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffSalary

