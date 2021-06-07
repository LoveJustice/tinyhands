from django.contrib import admin
from budget.models import BorderStationBudgetCalculation, OtherBudgetItemCost


class BorderStationBudgetCalculationAdminModel(admin.ModelAdmin):
    model = BorderStationBudgetCalculation
    search_fields = ['border_station', 'month_year', 'mdf_uuid']
    list_display = ['border_station', 'month_year', 'mdf_uuid']


class OtherBudgetItemCostAdminModel(admin.ModelAdmin):
    model = OtherBudgetItemCost
    search_fields = ['budget_item_parent', 'form_section', 'name', 'cost']
    list_display = ['budget_item_parent', 'form_section', 'name', 'cost']


admin.site.register(BorderStationBudgetCalculation, BorderStationBudgetCalculationAdminModel)
admin.site.register(OtherBudgetItemCost, OtherBudgetItemCostAdminModel)




