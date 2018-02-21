from django.contrib import admin
from budget.models import BorderStationBudgetCalculation, OtherBudgetItemCost, StaffSalary


class BorderStationBudgetCalculationAdminModel(admin.ModelAdmin):
    model = BorderStationBudgetCalculation
    search_fields = ['border_station', 'month_year', 'mdf_uuid']
    list_display = ['border_station', 'month_year', 'mdf_uuid']


class OtherBudgetItemCostAdminModel(admin.ModelAdmin):
    model = OtherBudgetItemCost
    search_fields = ['budget_item_parent', 'form_section', 'name', 'cost']
    list_display = ['budget_item_parent', 'form_section', 'name', 'cost']


class StaffSalaryAdminModel(admin.ModelAdmin):
    model = StaffSalary
    search_fields = ['budget_calc_sheet', 'salary', 'staff_person']
    list_display = ['budget_calc_sheet', 'salary', 'staff_person']


admin.site.register(BorderStationBudgetCalculation, BorderStationBudgetCalculationAdminModel)
admin.site.register(OtherBudgetItemCost, OtherBudgetItemCostAdminModel)
admin.site.register(StaffSalary, StaffSalaryAdminModel)




