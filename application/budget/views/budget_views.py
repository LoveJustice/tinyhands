import datetime

from dateutil.relativedelta import relativedelta
from django.db.models import Count, Sum
from rest_framework import filters, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from budget.models import BorderStationBudgetCalculation, OtherBudgetItemCost, StaffSalary
from budget.serializers import BorderStationBudgetCalculationSerializer, OtherBudgetItemCostSerializer, StaffSalarySerializer, BorderStationBudgetCalculationListSerializer
from dataentry.models import InterceptionRecord
from rest_api.authentication import HasPermission
from static_border_stations.models import BorderStation


class BudgetViewSet(viewsets.ModelViewSet):
    queryset = BorderStationBudgetCalculation.objects.all()
    serializer_class = BorderStationBudgetCalculationSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    permissions_required = ['permission_budget_view']
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

    border_station = BorderStation.objects.get(pk=pk)
    staff_count = border_station.staff_set.count()

    # Last month data will count records from the 15th of previous month to 14th of budget sheet month
    all_interception_records = InterceptionRecord.objects.annotate(interceptee_count=Count("interceptees")).filter(irf_number__startswith=border_station.station_code)
    last_months = all_interception_records.filter(date_time_of_interception__gte=(date+relativedelta(months=-1)), date_time_of_interception__lte=date)
    last_3_months = all_interception_records.filter(date_time_of_interception__gte=(date+relativedelta(months=-3)), date_time_of_interception__lte=date)

    last_months_count = last_months.aggregate(total=Sum('number_of_victims'))
    last_3_months_count = last_3_months.aggregate(total=Sum('number_of_victims'))
    all_interception_records_count = all_interception_records.aggregate(total=Sum('number_of_victims'))
    
    if budget_sheets:  # If this border station has had a previous budget calculation worksheet
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
        {"all": all_interception_records_count['total'],
         "all_cost": 0,
         "last_month": last_months_count['total'],
         "last_months_cost": 0,
         "last_3_months": last_3_months_count['total'],
         "last_3_months_cost": 0,
         "staff_count": staff_count,
         "last_months_total_cost": 0
         })


class OtherItemsViewSet(viewsets.ModelViewSet):
    queryset = OtherBudgetItemCost.objects.all()
    serializer_class = OtherBudgetItemCostSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    permissions_required = ['permission_budget_view']
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


class StaffSalaryViewSet(viewsets.ModelViewSet):
    queryset = StaffSalary.objects.all()
    serializer_class = StaffSalarySerializer
    permission_classes = [IsAuthenticated, HasPermission]
    permissions_required = ['permission_budget_view']

    def budget_calc_retrieve(self, request, *args, **kwargs):
        """
            Retrieve all of the staffSalaries for a particular budget calculation sheet
        """
        self.object_list = self.filter_queryset(self.get_queryset().filter(budget_calc_sheet=self.kwargs['parent_pk']))
        serializer = self.get_serializer(self.object_list, many=True)
        return Response(serializer.data)
