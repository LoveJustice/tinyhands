import StringIO
import datetime

from braces.views import LoginRequiredMixin
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views.generic import ListView, DeleteView, View
from lxml import etree
from rest_framework import filters, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from templated_email import send_templated_mail
from z3c.rml import document

from accounts.mixins import PermissionsRequiredMixin
from budget.models import BorderStationBudgetCalculation, OtherBudgetItemCost, StaffSalary
from dataentry.models import InterceptionRecord
from rest_api.authentication import HasPermission
from serializers import BorderStationBudgetCalculationSerializer, OtherBudgetItemCostSerializer, StaffSalarySerializer, BorderStationBudgetCalculationListSerializer
from static_border_stations.models import Staff, BorderStation, CommitteeMember
from static_border_stations.serializers import StaffSerializer, CommitteeMemberSerializer


class OldBudgetViewSet(viewsets.ModelViewSet):
    authentication_classes = [IsAuthenticated, HasPermission]
    permissions_required = ['permission_budget_manage']
    queryset = BorderStationBudgetCalculation.objects.all()
    serializer_class = BorderStationBudgetCalculationSerializer


class BudgetViewSet(viewsets.ModelViewSet):
    queryset = BorderStationBudgetCalculation.objects.all()
    serializer_class = BorderStationBudgetCalculationSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    permissions_required = ['permission_budget_manage']
    filter_backends = (filters.SearchFilter, filters.OrderingFilter,)
    search_fields = ['border_station__station_name', 'border_station__station_code']
    ordering_fields = ['border_station__station_name', 'border_station__station_code', 'month_year', 'date_time_entered', 'date_time_last_updated']

    def list(self, request, *args, **kwargs):
            temp = self.serializer_class
            self.serializer_class = BorderStationBudgetCalculationListSerializer  # we want to use a custom serializer just for the list view
            super_list_response = super(BudgetViewSet, self).list(request, *args, **kwargs)  # call the supers list view with custom serializer
            self.serializer_class = temp  # put the original serializer back in place
            return super_list_response


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def retrieve_latest_budget_sheet_for_border_station(request, pk):
    budget_sheet = BorderStationBudgetCalculation.objects.filter(border_station=pk).order_by('-date_time_entered').first()  # Get's you the latest budget sheet for a border stations

    if budget_sheet:  # if there has been a preview budget sheet

        other_items_serializer = OtherBudgetItemCostSerializer(budget_sheet.otherbudgetitemcost_set.all(), many=True)
        staff_serializer = StaffSalarySerializer(budget_sheet.staffsalary_set.all(), many=True)
        budget_serializer = BorderStationBudgetCalculationSerializer(budget_sheet)

        return Response(
            {
                "budget_form": budget_serializer.data,
                "other_items": other_items_serializer.data,
                "staff_salaries": staff_serializer.data
            }
        )
    # If there hasn't been a previous budget sheet
    return Response({"budget_form": {"border_station": pk}, "other_items": "", "staff_salaries": "", "None": 1})


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def previous_data(request, pk, month, year):
    date = datetime.datetime(int(year), int(month), 15)  # We pass the Month_year as two key-word arguments because the day is always 15
    budget_sheets = BorderStationBudgetCalculation.objects.filter(border_station=pk, month_year__lte=date).order_by('-date_time_entered')  # filter them so the first element is the most recent

    if budget_sheets:  # If this border station has had a previous budget calculation worksheet
        border_station = BorderStation.objects.get(pk=pk)
        staff_count = border_station.staff_set.count()

        all_interception_records = InterceptionRecord.objects.annotate(interceptee_count=Count("interceptees")).filter(irf_number__startswith=border_station.station_code)
        last_months = all_interception_records.filter(date_time_of_interception__gte=(date+relativedelta(months=-1)), date_time_of_interception__lte=date)
        last_3_months = all_interception_records.filter(date_time_of_interception__gte=(date+relativedelta(months=-3)), date_time_of_interception__lte=date)

        last_months_count = last_months.aggregate(total=Sum('number_of_victims'))
        last_3_months_count = last_3_months.aggregate(total=Sum('number_of_victims'))
        all_interception_records_count = all_interception_records.aggregate(total=Sum('number_of_victims'))

        last_3_months_count_divide = last_3_months_count['total']
        if last_3_months_count['total'] is None:
            last_3_months_count['total'] = 0
            last_3_months_count_divide = 1
        last_months_count_divide = last_months_count['total']
        if last_months_count['total'] is None:
            last_months_count['total'] = 0
            last_months_count_divide = 1
        all_interception_records_count_divide = all_interception_records_count['total']
        if all_interception_records_count['total'] is None:
            all_interception_records_count['total'] = 0
            all_interception_records_count_divide = 1

        last_3_months_cost = 0
        last_3_months_sheets = budget_sheets.filter(month_year__gte=date+relativedelta(months=-3))
        last_months_sheets = budget_sheets.filter(month_year__gte=date+relativedelta(months=-1))
        if last_months_sheets.count() > 0:
            last_months_cost = last_months_sheets[0].station_total()
        else:
            last_months_cost = 0
        for sheet in last_3_months_sheets:
            last_3_months_cost += sheet.station_total()
        all_cost = 0
        for sheet in budget_sheets:
            all_cost += sheet.station_total()
        return Response(
            {
                "all": all_interception_records_count['total'],
                "all_cost": all_cost/all_interception_records_count_divide,
                "last_month": last_months_count['total'],
                "last_months_cost": last_months_cost/last_months_count_divide,
                "last_3_months": last_3_months_count['total'],
                "last_3_months_cost": last_3_months_cost/last_3_months_count_divide,
                "staff_count": staff_count,
                "last_months_total_cost": last_months_cost
            }
        )
    # If this border station has not had a previous budget calculation worksheet
    return Response(
        {"all": 0,
         "all_cost": 0,
         "last_month": 0,
         "last_months_cost": 0,
         "last_3_months": 0,
         "last_3_months_cost": 0,
         "staff_count": 0,
         "last_months_total_cost": 0
         })


def ng_budget_calc_update(request, pk):
    if not request.user.permission_budget_manage:
        return redirect("home")

    border_station = BorderStationBudgetCalculation.objects.get(pk=pk).border_station
    submit_type = 2
    return render(request, 'budget/borderstationbudgetcalculation_form.html', locals())


def ng_budget_calc_create(request, pk):
    if not request.user.permission_budget_manage:
        return redirect("home")

    border_station = BorderStation.objects.get(pk=pk)
    submit_type = 1
    return render(request, 'budget/borderstationbudgetcalculation_form.html', locals())


def ng_budget_calc_view(request, pk):
    if not request.user.permission_budget_manage:
        return redirect("home")

    border_station = BorderStationBudgetCalculation.objects.get(pk=pk).border_station
    submit_type = 3
    return render(request, 'budget/borderstationbudgetcalculation_form.html', locals())


class OldOtherItemsViewSet(viewsets.ModelViewSet):
    queryset = OtherBudgetItemCost.objects.all()
    serializer_class = OtherBudgetItemCostSerializer
    authentication_classes = [IsAuthenticated, HasPermission]
    permissions_required = ['permission_budget_manage']

    def retrieve(self, request, *args, **kwargs):
        """
            I'm overriding this method to retrieve all
            of the budget items for a particular budget calculation sheet
        """
        self.object_list = self.filter_queryset(self.get_queryset().filter(budget_item_parent=self.kwargs['pk']))
        serializer = self.get_serializer(self.object_list, many=True)
        return Response(serializer.data)

    @list_route()
    def list_by_budget_sheet(self, request, parent_pk, *args, **kwargs):
        other_items_list = OtherBudgetItemCost.objects.filter(budget_item_parent_id=parent_pk)
        serializer = self.get_serializer(other_items_list, many=True)
        return Response(serializer.data)


class OtherItemsViewSet(viewsets.ModelViewSet):
    queryset = OtherBudgetItemCost.objects.all()
    serializer_class = OtherBudgetItemCostSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    permissions_required = ['permission_budget_manage']
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('form_section',)

    def list(self, request, *args, **kwargs):
        """
            I'm overriding this method to retrieve all
            of the budget items for a particular budget calculation sheet
        """
        self.object_list = self.filter_queryset(self.get_queryset().filter(budget_item_parent=self.kwargs['parent_pk']))
        serializer = self.get_serializer(self.object_list, many=True)
        return Response(serializer.data)

    @list_route()
    def list_by_budget_sheet(self, request, parent_pk, *args, **kwargs):
        other_items_list = OtherBudgetItemCost.objects.filter(budget_item_parent_id=parent_pk)
        serializer = self.get_serializer(other_items_list, many=True)
        return Response(serializer.data)


class OldStaffSalaryViewSet(viewsets.ModelViewSet):
    queryset = StaffSalary.objects.all()
    serializer_class = StaffSalarySerializer
    authentication_classes = [IsAuthenticated, HasPermission]
    permissions_required = ['permission_budget_manage']


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


class StaffSalaryViewSet(viewsets.ModelViewSet):
    queryset = StaffSalary.objects.all()
    serializer_class = StaffSalarySerializer
    authentication_classes = [IsAuthenticated, HasPermission]
    permissions_required = ['permission_budget_manage']

    def budget_calc_retrieve(self, request, *args, **kwargs):
        """
            Retrieve all of the staffSalaries for a particular budget calculation sheet
        """
        self.object_list = self.filter_queryset(self.get_queryset().filter(budget_calc_sheet=self.kwargs['parent_pk']))
        serializer = self.get_serializer(self.object_list, many=True)
        return Response(serializer.data)


class BudgetCalcListView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        ListView):
    model = BorderStationBudgetCalculation
    border_stations = BorderStation.objects.all()
    queryset = BorderStationBudgetCalculation.objects.all().order_by('-month_year')
    permissions_required = ['permission_budget_manage']

    def get_context_data(self, **kwargs):
        context = super(BudgetCalcListView, self).get_context_data(**kwargs)
        if BorderStationBudgetCalculation.objects.all().count() == 0:
            context["none_in_system"] = True
        return context


class BudgetCalcDeleteView(DeleteView, LoginRequiredMixin, PermissionsRequiredMixin):
    model = BorderStationBudgetCalculation
    permissions_required = ['permission_budget_manage']
    success_url = reverse_lazy('budget_list')

    def delete(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
            return super(BudgetCalcDeleteView, self).delete(request)
        else:
            messages.error(request, "You have no power here!!!")


class MoneyDistribution(viewsets.ViewSet):
    authentication_classes = [IsAuthenticated, HasPermission]
    permissions_required = ['permission_budget_manage']

    def retrieve(self, request, pk):
        border_station = BorderStationBudgetCalculation.objects.get(pk=pk).border_station
        staff = border_station.staff_set.all().filter(receives_money_distribution_form=True)
        committee_members = border_station.committeemember_set.all().filter(receives_money_distribution_form=True).all()

        staff_serializer = StaffSerializer(staff, many=True)
        committee_members_serializer = CommitteeMemberSerializer(committee_members, many=True)

        pdf_url = settings.SITE_DOMAIN + reverse('MdfPdf', kwargs={"pk": pk})

        return Response({"staff_members": staff_serializer.data, "committee_members": committee_members_serializer.data, "pdf_url": pdf_url})

    def send_emails(self, request, pk):
        staff_ids = request.data['staff_ids']
        budget_calc_id = pk
        committee_ids = request.data['committee_ids']

        # send the emails
        for id in staff_ids:
            person = Staff.objects.get(pk=id)
            self.email_staff_and_committee_members(person, budget_calc_id, 'money_distribution_form')

        for id in committee_ids:
            person = CommitteeMember.objects.get(pk=id)
            self.email_staff_and_committee_members(person, budget_calc_id, 'money_distribution_form')

        return Response("Emails Sent!", status=200)

    def email_staff_and_committee_members(self, person, budget_calc_id, template, context={}):
        context['person'] = person
        context['budget_calc_id'] = budget_calc_id
        context['site'] = settings.SITE_DOMAIN
        send_templated_mail(
            template_name=template,
            from_email=settings.ADMIN_EMAIL_SENDER,
            recipient_list=[person.email],
            context=context
        )


class PDFView(View, LoginRequiredMixin, PermissionsRequiredMixin):
    permissions_required = ['permission_budget_manage']
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
        response['X-Frame-Options'] = "*"

        doc.process(response)
        return response


class MoneyDistributionFormPDFView(PDFView, LoginRequiredMixin, PermissionsRequiredMixin):
    permissions_required = ['permission_budget_manage']
    template_name = 'budget/MoneyDistributionTemplate.rml'
    filename = 'Monthly-Money-Distribution-Form.pdf'

    def get_context_data(self):

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
            'salary_total': station.salary_total(),
            'travel_chair_bool': station.travel_chair_with_bike,
            'travel_chair': station.travel_chair_with_bike_amount,
            'travel_manager_bool': station.travel_manager_with_bike,
            'travel_manager': station.travel_manager_with_bike_amount,
            'travel_total': station.travel_total(),

            'communication_chair_bool': station.communication_chair,
            'communication_chair': station.communication_chair_amount,
            'communication_manager_bool': station.communication_manager,
            'communication_manager': station.communication_manager_amount,
            'communication_staff': station.communication_staff_total(),
            'communication_total': station.communication_total(),

            'admin_meetings': station.administration_number_of_meetings_per_month * station.administration_number_of_meetings_per_month_multiplier,
            'admin_total': station.administration_total(),

            'medical_total': station.medical_total(),

            'misc_total': station.miscellaneous_total(),

            'shelter_total': station.shelter_total(),

            'food_and_gas_intercepted_girls': station.food_and_gas_number_of_intercepted_girls_multiplier_before * station.food_and_gas_number_of_intercepted_girls * station.food_and_gas_number_of_intercepted_girls_multiplier_after,
            'food_and_gas_limbo_girls': station.food_and_gas_limbo_girls_multiplier * station.food_and_gas_number_of_limbo_girls * station.food_and_gas_number_of_days,
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
    if not request.user.permission_budget_manage:
        return redirect("home")
    border_station = (BorderStationBudgetCalculation.objects.get(pk=pk)).border_station
    return render(request, 'budget/moneydistribution_view.html', locals())
