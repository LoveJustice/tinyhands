import StringIO
import datetime

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
from django.conf import settings


from braces.views import LoginRequiredMixin
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from templated_email import send_templated_mail

from budget.forms import BorderStationBudgetCalculationForm
from budget.models import BorderStationBudgetCalculation, OtherBudgetItemCost, StaffSalary
from dataentry.models import InterceptionRecord
from static_border_stations.models import Staff, BorderStation, CommitteeMember
from serializers import BorderStationBudgetCalculationSerializer, OtherBudgetItemCostSerializer, StaffSalarySerializer
from models import BorderStationBudgetCalculation
from z3c.rml import rml2pdf, document
from lxml import etree
from rest_framework import generics, viewsets
from reportlab import *
from static_border_stations.serializers import StaffSerializer, CommitteeMemberSerializer


class BudgetViewSet(viewsets.ModelViewSet):
    queryset = BorderStationBudgetCalculation.objects.all()
    serializer_class = BorderStationBudgetCalculationSerializer


class MoneyDistribution(viewsets.ViewSet):
    def get_people_needing_form(self, request, pk):
        border_station = BorderStation.objects.get(pk=pk)
        staff = border_station.staff_set.all().filter(receives_money_distribution_form=True)
        committee_members = border_station.committeemember_set.all().filter(receives_money_distribution_form=True).all()

        staff_serializer = StaffSerializer(staff, many=True)
        committee_members_serializer = CommitteeMemberSerializer(committee_members, many=True)
        return Response({"staff_members": staff_serializer.data, "committee_members": committee_members_serializer.data})

    def send_emails(self, request, *args, **kwargs):
        import ipdb
        ipdb.set_trace()
        staff_ids = request.DATA['staff_ids']
        committee_ids = request.DATA['committee_ids']

        file = ""
        # send the emails
        for id in staff_ids:
            person = Staff.objects.get(pk=id)
            self.email_staff_and_committee_members(person, file, 'money_distribution_form')

        for id in committee_ids:
            person = CommitteeMember.objects.get(pk=id)
            self.email_staff_and_committee_members(person, file, 'money_distribution_form')

        return Response("Emails Sent!", status=200)

    def email_staff_and_committee_members(self, person, pdf_file, template, context={}):
        context['person'] = person
        send_templated_mail(
            template_name=template,
            from_email=settings.ADMIN_EMAIL_SENDER,
            recipient_list=[person.email],
            context=context
        )



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
                "staff_salaries": staff_serializer.data,
                "last_months_total_cost": budget_sheet.station_total()
            }
        )
    return Response({"budget_form": {"border_station": pk}, "other_items": "", "staff_salaries": ""})

@api_view(['GET'])
def previous_data(request, pk):
    budget_sheet = BorderStationBudgetCalculation.objects.filter(border_station=pk).order_by('-date_time_entered').first()



    if budget_sheet:
        border_station = BorderStation.objects.get(pk=pk)
        staff_count = border_station.staff_set.count()

        all_interception_records = InterceptionRecord.objects.filter(irf_number__startswith=border_station.station_code)
        last_months = all_interception_records.filter(date_time_of_interception__gte=(datetime.datetime.now() - datetime.timedelta(1*365/12)))
        last_3_months = all_interception_records.filter(date_time_of_interception__gte=(datetime.datetime.now() - datetime.timedelta(3*365/12)))




    # all the interception records that start with the station code > a specific date (so we can develop a function for it)
        # iterate over each record, count their interceptees and add them to the sum
    return Response(
        {
            "all": 5,
            "all_cost": 6,
            "last_month": 1,
            "last_months_cost": 2,
            "last_3_months": 3,
            "last_3_months_cost": 4,
            "staff_count": 10
        }
    )


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
