from django import forms
from budget.models import BorderStationBudgetCalculation, OtherBudgetItemCost
from django.forms.models import inlineformset_factory
from static_border_stations.models import Staff

class BorderStationBudgetCalculationForm(forms.ModelForm):
    class Meta:
        model = BorderStationBudgetCalculation

#StaffFormSet = inlineformset_factory(BorderStationBudgetCalculation, Staff, exclude=[], extra=9)

class OtherBudgetItemCostForm(forms.ModelForm):
    class Meta:
        model = OtherBudgetItemCost