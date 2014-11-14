from braces.views import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView
from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet
# from budget.models import InterceptionRecordListView
from accounts.mixins import PermissionsRequiredMixin
from budget.forms import BorderStationBudgetCalculationForm
from budget.models import BorderStationBudgetCalculation, OtherBudgetItemCost


class OtherBudgetItemCostFormInline(InlineFormSet):
    model = OtherBudgetItemCost


class BudgetCalcCreateView(
        LoginRequiredMixin,
        CreateWithInlinesView):
    model = BorderStationBudgetCalculation
    template_name = 'budget/budget_calculation_form.html'
    form_class = BorderStationBudgetCalculationForm
    success_url = reverse_lazy('home')
    inlines = [OtherBudgetItemCostFormInline]


class BudgetCalcListView(
        LoginRequiredMixin,
        ListView):
    model = BorderStationBudgetCalculation