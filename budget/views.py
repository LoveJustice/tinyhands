import StringIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse_lazy
from django.forms import formset_factory, inlineformset_factory
from django.forms.models import modelformset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect, render_to_response
from django.template.loader import render_to_string
from django.views.generic import ListView, DeleteView, View


from braces.views import LoginRequiredMixin
from rest_framework.decorators import api_view
from rest_framework.response import Response

from budget.forms import BorderStationBudgetCalculationForm
from budget.models import BorderStationBudgetCalculation, OtherBudgetItemCost, StaffSalary
from static_border_stations.models import Staff, BorderStation
from serializers import BorderStationBudgetCalculationSerializer, OtherBudgetItemCostSerializer, StaffSalarySerializer
from models import BorderStationBudgetCalculation
from z3c.rml import rml2pdf, document
from lxml import etree
from rest_framework import generics, viewsets
import ipdb
from reportlab import *


class BudgetViewSet(viewsets.ModelViewSet):
    queryset = BorderStationBudgetCalculation.objects.all()
    serializer_class = BorderStationBudgetCalculationSerializer


@api_view(['GET'])
def retrieve_latest_budget_sheet_for_border_station(request, pk):
    budget_sheet = BorderStationBudgetCalculation.objects.filter(border_station=pk).order_by('-date_time_entered').first()

    if budget_sheet:

        other_items_serializer = OtherBudgetItemCostSerializer(budget_sheet.otherbudgetitemcost_set.all())
        staff_serializer = StaffSalarySerializer(budget_sheet.staffsalary_set.all())
        budget_serializer = BorderStationBudgetCalculationSerializer(budget_sheet)

        return Response(
            {
                "budget_form": budget_serializer.data,
                "other_items": other_items_serializer.data,
                "staff_salaries": staff_serializer.data
            }
        )
    return Response({"budget_form": {"border_station": pk}, "other_items": "", "staff_salaries": ""})



def ng_budget_calc_update(request, pk):
    #is there a better way to do permissions in function based views? Yes
    if not request.user.permission_budget_manage:
        return redirect("home")

    border_station = BorderStationBudgetCalculation.objects.get(pk=pk).border_station
    submit_type = 2
    return render(request, 'budget/borderstationbudgetcalculation_form.html', locals())


def ng_budget_calc_create(request, pk):
    #is there a better way to do permissions in function based views?
    if not request.user.permission_budget_manage:
        return redirect("home")

    border_station = BorderStation.objects.get(pk=pk)
    submit_type = 1
    return render(request, 'budget/borderstationbudgetcalculation_form.html', locals())


def ng_budget_calc_view(request, pk):
    """
        is there a better way to do permissions in function based views?
    """
    if not request.user.permission_budget_manage:
        return redirect("home")

    border_station = BorderStationBudgetCalculation.objects.get(pk=pk).border_station
    submit_type = 3
    return render(request, 'budget/borderstationbudgetcalculation_form.html', locals())


class OtherItemsViewSet(viewsets.ModelViewSet):
    queryset = OtherBudgetItemCost.objects.all()
    serializer_class = OtherBudgetItemCostSerializer

    def retrieve(self, request, *args, **kwargs):
        """
            I'm overriding this method to retrieve all
            of the budget items for a particular budget calculation sheet
        """
        self.object_list = self.filter_queryset(self.get_queryset().filter(budget_item_parent=self.kwargs['pk']))
        serializer = self.get_serializer(self.object_list, many=True)
        return Response(serializer.data)


class StaffSalaryViewSet(viewsets.ModelViewSet):
    queryset = StaffSalary.objects.all()
    serializer_class = StaffSalarySerializer


    def budget_calc_retrieve(self, request, *args, **kwargs):
        """
            Retrieve all of the staffSalaries for a particular budget calculation sheet
        """
        budget_sheet = BorderStationBudgetCalculation.objects.filter(border_station=self.kwargs['pk']).order_by('-date_time_entered').first()
        if budget_sheet:
            staff_set = budget_sheet.staffsalary_set.all()
            serializer = self.get_serializer(staff_set, many=True)
            return Response(serializer.data)
        else:
            self.object_list = self.filter_queryset(self.get_queryset().filter(budget_calc_sheet=self.kwargs['pk']))
            serializer = self.get_serializer(self.object_list, many=True)
            return Response(serializer.data)


class BudgetCalcListView(
        LoginRequiredMixin,
        ListView):
    model = BorderStationBudgetCalculation
    border_stations = BorderStation.objects.all()
    permissions_required = ['permission_budget_manage']

    def get_context_data(self, **kwargs):
        context = super(BudgetCalcListView, self).get_context_data(**kwargs)
        if BorderStationBudgetCalculation.objects.all().count()==0:
            context["none_in_system"] = True
        return context


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

        self.rml = render_to_string(self.template_name, self.get_context_data())

        buf.write(rml)
        buf.seek(0)
        root = etree.parse(buf).getroot()
        doc = document.Document(root)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = "filename=%s" % self.get_filename()
        doc.process(response)

        return response


class MoneyDistributionFormPDFView(PDFView):
    template_name = 'budget/MoneyDistributionTemplate.rml'
    filename = 'Monthly-Money-Distribution-Form.pdf'

    def get_context_data(self):
        # application = LoanApplication.objects.get(
            # pk=self.kwargs['application_id'])

        station = BorderStationBudgetCalculation.objects.get(pk=self.kwargs['pk'])
        staffSalaries = StaffSalary.objects.filter(budget_calc_sheet=self.kwargs['pk'])
        otherItems = station.otherbudgetitemcost_set.all()

        adminMeetings = station.administration_number_of_meetings_per_month * station.administration_number_of_meetings_per_month_multiplier

        return {
            'otherItems': otherItems,
            'name': station.border_station.station_name,
            'date': station.date_time_entered.date,
            'number': len(staffSalaries),
            'staffSalaries': staffSalaries,

            'travel_chair_bool': station.travel_chair_with_bike,
            'travel_chair': station.travel_chair_with_bike_amount,
            'travel_manager_bool': station.travel_manager_with_bike,
            'travel_manager': station.travel_manager_with_bike_amount,
            'travel_total': station.travel_total(),

            'communication_chair_bool': station.communication_chair,
            'communication_chair': station.communication_chair_amount,
            'communication_manager_bool': station.communication_manager,
            'communication_manager': station.communication_manager_amount,
            'communication_total': station.communication_total(),

            'admin_meetings': adminMeetings,
            'admin_total': station.administration_total(),

            'medical_total': station.medical_total(),

            'misc_total': station.miscellaneous_total(),

            'shelter_total': station.shelter_total(),

            'food_and_gas_intercepted_girls': station.food_and_gas_number_of_intercepted_girls,
            'food_and_gas_limbo_girls': station.food_and_gas_number_of_limbo_girls,
            'food_gas_total': station.food_and_gas_total(),

            'awareness_contact_cards_bool': station.awareness_contact_cards,
            'awareness_contact_cards': station.awareness_contact_cards_amount,
            'awareness_awareness_party_bool': station.awareness_awareness_party_boolean,
            'awareness_awareness_party': station.awareness_awareness_party,
            'awareness_sign_boards_bool': station.awareness_sign_boards_boolean,
            'awareness_sign_boards': station.awareness_sign_boards,
            'awareness_total': station.awareness_total(),

            'supplies_walkie_talkies_bool': station.supplies_walkie_talkies_boolean,
            'supplies_walkie_talkies': station.supplies_walkie_talkies_amount,
            'supplies_recorders_bool': station.supplies_recorders_boolean,
            'supplies_recorders': station.supplies_recorders_amount,
            'supplies_binoculars_bool': station.supplies_binoculars_boolean,
            'supplies_binoculars': station.supplies_binoculars_amount,
            'supplies_flashlights_bool': station.supplies_flashlights_boolean,
            'supplies_flashlights': station.supplies_flashlights_amount,
            'supplies_total': station.supplies_total,

            'monthly_total': station.station_total()
        }

@login_required
def money_distribution_view(request, pk):
    id = pk
    return render(request, 'budget/moneydistribution_view.html', locals())

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
    permissions_required = ['permission_budget_manage']
    success_url = reverse_lazy('budget_list')

    def delete(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
            return super(BudgetCalcDeleteView, self).delete(request)
        else:
            messages.error(request, "You have no power here!!!")
