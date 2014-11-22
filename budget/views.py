from braces.views import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.forms import formset_factory
from django.forms.models import modelformset_factory
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DeleteView
from budget.forms import BorderStationBudgetCalculationForm, OtherBudgetItemCostForm
from budget.models import BorderStationBudgetCalculation, OtherBudgetItemCost
from static_border_stations.models import Staff, BorderStation


@login_required
def budget_calc_create(request, pk):
    border_station = get_object_or_404(BorderStation, pk=pk)
    border_station_staff = border_station.staff_set.all()
    form = BorderStationBudgetCalculationForm()

    StaffFormSet = modelformset_factory(model=Staff, extra=0)

    travel_items_formset = formset_factory(OtherBudgetItemCostForm, extra=1)
    misc_items_formset = formset_factory(OtherBudgetItemCostForm, extra=1)
    awareness_items_formset = formset_factory(OtherBudgetItemCostForm, extra=1)
    supplies_items_formset = formset_factory(OtherBudgetItemCostForm, extra=1)

    if request.method == "POST":
        staff_formset = StaffFormSet(request.POST or None, queryset=border_station_staff)
        form = BorderStationBudgetCalculationForm(request.POST)

        travel_items_formset = travel_items_formset(request.POST)
        misc_items_formset = misc_items_formset(request.POST)
        awareness_items_formset = awareness_items_formset(request.POST)
        supplies_items_formset = supplies_items_formset(request.POST)

        import ipdb
        ipdb.set_trace()
        # if form.is_valid() and staff_formset.is_valid() and misc_items_formset.is_valid():
        if form.is_valid() and misc_items_formset.is_valid():
            form.instance.border_station = border_station
            form.save()
            # staff_formset.save()

            all_valid(misc_items_formset, 2, form.instance)

            return redirect("budget_list")

    staff_formset = StaffFormSet(queryset=border_station_staff)



    submit_type = "Create"
    return render(request, 'budget/borderstationbudgetcalculation_form.html', locals())


@login_required
def budget_calc_update(request, pk):
    budget_calc = get_object_or_404(BorderStationBudgetCalculation, pk=pk)
    form = BorderStationBudgetCalculationForm(instance=budget_calc)



    border_station = budget_calc.border_station
    border_station_staff = border_station.staff_set.all()
    StaffFormSet = modelformset_factory(model=Staff, extra=0)

    OtherItemsFormset = modelformset_factory(model=OtherBudgetItemCost, extra=1)

    if request.method == "POST":
        staff_formset = StaffFormSet(request.POST, queryset=border_station_staff)

        misc_items_formset = OtherItemsFormset(request.POST or None, queryset=budget_calc.otherbudgetitemcost_set.filter(form_section=2))

        form = BorderStationBudgetCalculationForm(request.POST, instance=budget_calc)


        import ipdb
        ipdb.set_trace()
        if form.is_valid() and staff_formset.is_valid() and misc_items_formset:
            form.instance.border_station = border_station
            form.save()
            staff_formset.save()
            misc_items_formset.save()
            return redirect("budget_list")

    staff_formset = StaffFormSet(queryset=border_station_staff)

    travel_items_formset = OtherItemsFormset(queryset=budget_calc.otherbudgetitemcost_set.filter(form_section=1))
    misc_items_formset = OtherItemsFormset(queryset=budget_calc.otherbudgetitemcost_set.filter(form_section=2))
    awareness_items_formset = OtherItemsFormset(queryset=budget_calc.otherbudgetitemcost_set.filter(form_section=3))
    supplies_items_formset = OtherItemsFormset(queryset=budget_calc.otherbudgetitemcost_set.filter(form_section=4))

    submit_type = "Update"
    return render(request, 'budget/borderstationbudgetcalculation_form.html', locals())


class BudgetCalcListView(
        LoginRequiredMixin,
        ListView):
    model = BorderStationBudgetCalculation


@login_required
def budget_calc_view(request, pk):
    budget_calc = get_object_or_404(BorderStationBudgetCalculation, pk=pk)
    form = BorderStationBudgetCalculationForm(instance=budget_calc)


    border_station = budget_calc.border_station
    border_station_staff = border_station.staff_set.all()

    StaffFormSet = modelformset_factory(model=Staff, extra=0)
    staff_formset = StaffFormSet(queryset=border_station_staff)

    return render(request, 'budget/borderstationbudgetcalculation_form.html', locals())


class BudgetCalcDeleteView(DeleteView, LoginRequiredMixin):
    model = BorderStationBudgetCalculation
    success_url = reverse_lazy('budget_list')

    def delete(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
            return super(BudgetCalcDeleteView, self).delete(request)
        else:
            messages.error(request, "You have no power here!!!")


def all_valid(formset, form_section, budget_calc):
    for form in formset:
        form.instance.budget_item_parent = budget_calc
        form.instance.form_section = form_section
        form.save()