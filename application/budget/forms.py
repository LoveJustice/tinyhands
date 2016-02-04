from django import forms
from budget.models import BorderStationBudgetCalculation, OtherBudgetItemCost


class BorderStationBudgetCalculationForm(forms.ModelForm):
    class Meta:
        model = BorderStationBudgetCalculation
        exclude = ['border_station']


class OtherBudgetItemCostForm(forms.ModelForm):
    class Meta:
        model = OtherBudgetItemCost
        fields = ['name', 'cost']
