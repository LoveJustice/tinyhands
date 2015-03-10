import StringIO
from braces.views import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse_lazy
from django.forms import formset_factory, inlineformset_factory
from django.forms.models import modelformset_factory
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DeleteView
from budget.forms import BorderStationBudgetCalculationForm, OtherBudgetItemCostForm
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect, render_to_response
from django.template.loader import render_to_string
from django.views.generic import ListView, DeleteView, View
from budget.forms import BorderStationBudgetCalculationForm
from budget.models import BorderStationBudgetCalculation, OtherBudgetItemCost
from static_border_stations.models import Staff, BorderStation

from z3c.rml import rml2pdf, document
from lxml import etree
from reportlab import *


@login_required
def budget_calc_create_rest(request, pk):


@login_required
def budget_calc_create(request, pk):
    #is there a better way to do permissions in function based views?
    if not request.user.permission_budget_manage:
        return redirect("home")

    border_station = get_object_or_404(BorderStation, pk=pk)
    border_station_staff = border_station.staff_set.all()
    form = BorderStationBudgetCalculationForm()

    StaffFormSet = modelformset_factory(model=Staff, extra=0, fields=['salary'])

    OtherItemsFormset = inlineformset_factory(BorderStationBudgetCalculation, OtherBudgetItemCost, extra=1, fields=['name', 'cost'])

    if request.method == "POST":
        staff_formset = StaffFormSet(request.POST, queryset=border_station_staff, prefix='staff')
        form = BorderStationBudgetCalculationForm(request.POST)

        travel_items_formset = OtherItemsFormset(request.POST, prefix='travel')
        misc_items_formset = OtherItemsFormset(request.POST, prefix='misc')
        awareness_items_formset = OtherItemsFormset(request.POST, prefix='awareness')
        supplies_items_formset = OtherItemsFormset(request.POST, prefix='supplies')

        if form.is_valid() and staff_formset.is_valid() and travel_items_formset.is_valid() and misc_items_formset.is_valid() and awareness_items_formset.is_valid() and supplies_items_formset.is_valid():
            form.instance.border_station = border_station
            form.save()
            staff_formset.save()

            save_all(travel_items_formset, 1, form)
            save_all(misc_items_formset, 2, form)
            save_all(awareness_items_formset, 3, form)
            save_all(supplies_items_formset, 4, form)

            return redirect("budget_list")

    else:
        staff_formset = StaffFormSet(queryset=border_station_staff, prefix='staff')

        travel_items_formset = OtherItemsFormset(prefix='travel')
        misc_items_formset = OtherItemsFormset(prefix='misc')
        awareness_items_formset = OtherItemsFormset(prefix='awareness')
        supplies_items_formset = OtherItemsFormset(prefix='supplies')

    submit_type = "Create"
    return render(request, 'budget/borderstationbudgetcalculation_form.html', locals())


def save_all(other_formset, form_section, budget_calc_form):
    for form in other_formset:
        form.instance.budget_item_parent = budget_calc_form.instance
        form.instance.form_section = form_section
        if form.instance.cost > 0 or form.instance.name != '':
            form.save()
        if form.cleaned_data:
            if form.cleaned_data["DELETE"]:
                form.instance.delete()
    return True


@login_required
def budget_calc_update(request, pk):
    #is there a better way to do permissions in function based views?
    if not request.user.permission_budget_manage:
        return redirect("home")

    budget_calc = get_object_or_404(BorderStationBudgetCalculation, pk=pk)
    form = BorderStationBudgetCalculationForm(instance=budget_calc)

    border_station = budget_calc.border_station
    border_station_staff = border_station.staff_set.all()
    StaffFormSet = modelformset_factory(model=Staff, extra=0, fields=['salary'])

    OtherItemsFormset = inlineformset_factory(BorderStationBudgetCalculation, OtherBudgetItemCost, extra=1, fields=['name', 'cost'])

    if request.method == "POST":
        staff_formset = StaffFormSet(request.POST, queryset=border_station_staff, prefix='staff')
        form = BorderStationBudgetCalculationForm(request.POST, instance=budget_calc, empty_permitted=True)

        travel_items_formset = OtherItemsFormset(request.POST, instance=budget_calc, queryset=budget_calc.otherbudgetitemcost_set.filter(form_section=1), prefix='travel')
        misc_items_formset = OtherItemsFormset(request.POST, instance=budget_calc, queryset=budget_calc.otherbudgetitemcost_set.filter(form_section=2), prefix='misc')
        awareness_items_formset = OtherItemsFormset(request.POST, instance=budget_calc, queryset=budget_calc.otherbudgetitemcost_set.filter(form_section=3), prefix='awareness')
        supplies_items_formset = OtherItemsFormset(request.POST, instance=budget_calc, queryset=budget_calc.otherbudgetitemcost_set.filter(form_section=4), prefix='supplies')

        if form.is_valid() and staff_formset.is_valid() and travel_items_formset.is_valid() and misc_items_formset.is_valid() and awareness_items_formset.is_valid() and supplies_items_formset.is_valid():
            form.save()
            staff_formset.save()

            save_all(travel_items_formset, 1, form)
            save_all(misc_items_formset, 2, form)
            save_all(awareness_items_formset, 3, form)
            save_all(supplies_items_formset, 4, form)

            return redirect("budget_list")
    else:
        staff_formset = StaffFormSet(queryset=border_station_staff, prefix='staff')

        travel_items_formset = OtherItemsFormset(instance=budget_calc, queryset=budget_calc.otherbudgetitemcost_set.filter(form_section=1), prefix='travel')
        misc_items_formset = OtherItemsFormset(instance=budget_calc, queryset=budget_calc.otherbudgetitemcost_set.filter(form_section=2), prefix='misc')
        awareness_items_formset = OtherItemsFormset(instance=budget_calc, queryset=budget_calc.otherbudgetitemcost_set.filter(form_section=3), prefix='awareness')
        supplies_items_formset = OtherItemsFormset(instance=budget_calc, queryset=budget_calc.otherbudgetitemcost_set.filter(form_section=4), prefix='supplies')

    submit_type = "Update"
    return render(request, 'budget/borderstationbudgetcalculation_form.html', locals())


class BudgetCalcListView(
        LoginRequiredMixin,
        ListView):
    model = BorderStationBudgetCalculation
    border_stations = BorderStation.objects.all()
    permissions_required = ['permission_budget_manage']



def search_form(request):
    return render_to_response('search_form.html')


class PDFView(View):

    filename = 'report.pdf'
    template_name = ''

    def get_filename(self):
        return self.filename

    def get_context_data(self):
        return {}

    def dispatch(self, request, *args, **kwargs):
        if self.template_name == '':
            raise ImproperlyConfigured(
                "A template_name must be specified for the rml template.")

        # Use StringIO and not cStringIO because cStringIO can't accept unicode characters
        buf = StringIO.StringIO()
        rml = render_to_string(self.template_name, self.get_context_data())

        buf.write(rml)
        buf.seek(0)
        root = etree.parse(buf).getroot()
        doc = document.Document(root)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = "filename=%s" % self.get_filename()
        doc.process(response)

        return response


class MoneyDistributionFormPDFView(PDFView):
    template_name = 'budget/test.rml'
    filename = 'Monthly-Money-Distribution-Form.pdf'

    def get_context_data(self):
        # application = LoanApplication.objects.get(
            # pk=self.kwargs['application_id'])

        station = BorderStation.objects.get(pk=self.kwargs['pk'])

        return {
            'name': station.station_name,
        }


class BudgetCalcDeleteView(DeleteView, LoginRequiredMixin):
    model = BorderStationBudgetCalculation
    permissions_required = ['permission_budget_manage']
    success_url = reverse_lazy('budget_list')

    def delete(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
            return super(BudgetCalcDeleteView, self).delete(request)
        else:
            messages.error(request, "You have no power here!!!")
