from django import forms
from budget.models import BorderStationBudgetCalculation, OtherBudgetItemCost


class BorderStationBudgetCalculationForm(forms.ModelForm):
    class Meta:
        model = BorderStationBudgetCalculation


class OtherBudgetItemCostForm(forms.ModelForm):
    class Meta:
        model = OtherBudgetItemCost