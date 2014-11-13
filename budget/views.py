from braces.views import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import ListView, View, DeleteView, CreateView, UpdateView
from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet
# from budget.models import InterceptionRecordListView

def budget_create(request):
    return render(request, 'budget/budget_calculation_form.html')

"""
class BudgetListView(
        LoginRequiredMixin,
        ListView):
    model = BorderStationBudgetCalculationForm
    paginate_by = 20
    """