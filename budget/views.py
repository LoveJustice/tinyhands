import StringIO
from braces.views import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse_lazy
from django.forms.models import modelformset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect, render_to_response
from django.template import Template, Context
from django.template.loader import render_to_string
from django.views.generic import ListView, DeleteView, View
from budget.forms import BorderStationBudgetCalculationForm
from budget.models import BorderStationBudgetCalculation, OtherBudgetItemCost
from static_border_stations.models import Staff, BorderStation

from z3c.rml import rml2pdf, document
from lxml import etree
from reportlab import *
import preppy


@login_required
def budget_calc_create(request, pk):
    border_station = get_object_or_404(BorderStation, pk=pk)
    border_station_staff = border_station.staff_set.all()
    form = BorderStationBudgetCalculationForm()

    StaffFormSet = modelformset_factory(model=Staff, extra=0)

    if request.method == "POST":
        staff_formset = StaffFormSet(request.POST or None, queryset=border_station_staff)
        form = BorderStationBudgetCalculationForm(request.POST)
        import ipdb
        ipdb.set_trace()
        if form.is_valid() and staff_formset.is_valid():
            form.instance.border_station = border_station
            form.save()
            staff_formset.save()
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

    if request.method == "POST":
        staff_formset = StaffFormSet(request.POST or None, queryset=border_station_staff)
        form = BorderStationBudgetCalculationForm(request.POST, instance=budget_calc)
        if form.is_valid() and staff_formset.is_valid():
            form.instance.border_station = border_station
            form.save()
            staff_formset.save()
            return redirect("budget_list")

    staff_formset = StaffFormSet(queryset=border_station_staff)

    submit_type = "Update"
    return render(request, 'budget/borderstationbudgetcalculation_form.html', locals())


class BudgetCalcListView(
        LoginRequiredMixin,
        ListView):
    model = BorderStationBudgetCalculation

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
            #'interest_rate_100': application.interest_rate * 100,
            #'loan_amount_in_words': to_card(application.loan.amount),
        }

def getRML(name):
    """
    We used django template to write the RML, but you could use any other
    template language of your choice.
    """
    t = Template(open('budget/templates/budget/test.rml').read())
    c = Context({"name": name})
    rml = t.render(c)
    #django templates are unicode, and so need to be encoded to utf-8
    return rml.encode('utf8')

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
