from braces.views import LoginRequiredMixin
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView, DeleteView, CreateView
from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet
from extra_views.generic import GenericInlineFormSet
from rest_framework.exceptions import PermissionDenied
from budget.forms import BorderStationBudgetCalculationForm
from budget.models import BorderStationBudgetCalculation, OtherBudgetItemCost
from dataentry.forms import BorderStationForm
from static_border_stations.forms import StaffForm
from static_border_stations.models import Staff, BorderStation
from static_border_stations.views import StaffInline


class OtherBudgetItemCostFormInline(InlineFormSet):
    model = OtherBudgetItemCost


class BudgetCalcCreateView(CreateWithInlinesView, LoginRequiredMixin):
    model = BorderStation
    template_name = 'budget/borderstationbudgetcalculation_form.html'
    second_form_class = BorderStationForm
    form_class = BorderStationBudgetCalculationForm
    success_url = reverse_lazy('budget_list')

    def get_context_data(self, **kwargs):
        context = super(BudgetCalcCreateView, self).get_context_data(**kwargs)
        context['form2'] = self.second_form_class()
        context['form'] = self.form_class()
        return context


class BorderStationSetInline(InlineFormSet):
    model = BorderStation


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
