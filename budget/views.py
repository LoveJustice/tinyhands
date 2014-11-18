from braces.views import LoginRequiredMixin
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView, DeleteView
from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet
from rest_framework.exceptions import PermissionDenied
from budget.forms import BorderStationBudgetCalculationForm
from budget.models import BorderStationBudgetCalculation, OtherBudgetItemCost
from static_border_stations.models import Staff, BorderStation


class OtherBudgetItemCostFormInline(InlineFormSet):
    model = OtherBudgetItemCost


class BudgetCalcCreateView(
        LoginRequiredMixin,
        CreateWithInlinesView):
    model = BorderStationBudgetCalculation
    template_name = 'budget/borderstationbudgetcalculation_form.html'
    form_class = BorderStationBudgetCalculationForm
    success_url = reverse_lazy('budget_list')
    inlines = [OtherBudgetItemCostFormInline]


class BudgetCalcListView(
        LoginRequiredMixin,
        ListView):
    model = BorderStationBudgetCalculation


class BudgetCalcUpdateView(
        LoginRequiredMixin,
        UpdateWithInlinesView):
    model = BorderStationBudgetCalculation
    form_class = BorderStationBudgetCalculationForm
    success_url = reverse_lazy('budget_list')
    inlines = [OtherBudgetItemCostFormInline]


class BudgetCalcDetailView(BudgetCalcUpdateView, LoginRequiredMixin):
    def post(self, request, *args, **kwargs):
        raise PermissionDenied


class BudgetCalcDeleteView(DeleteView, LoginRequiredMixin):

    model = BorderStationBudgetCalculation
    success_url = reverse_lazy('budget_list')

    def delete(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
            return super(BudgetCalcDeleteView, self).delete(request)
        else:
            messages.error(request, "You have no power here!!!")
