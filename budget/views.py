from django.shortcuts import render
from django.views.generic import ListView, View, DeleteView, CreateView, UpdateView
from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet

# Create your views here.
def budget_create(request):
    return render(request,'budget/budget_calculation_form.html')