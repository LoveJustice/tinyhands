from django.forms import widgets
from rest_framework import serializers
from budget.models import BorderStationBudgetCalculation


class BorderStationBudgetCalculationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BorderStationBudgetCalculation