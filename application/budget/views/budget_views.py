import datetime

from dateutil.relativedelta import relativedelta
from django.db.models import Count, Sum
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import filters as fs
from django_filters import rest_framework as filters
from django.db.models import Q

from budget.models import BorderStationBudgetCalculation, OtherBudgetItemCost, StaffBudgetItem
from budget.serializers import BorderStationBudgetCalculationSerializer, OtherBudgetItemCostSerializer, StaffBudgetItemSerializer, BorderStationBudgetCalculationListSerializer
from dataentry.models import Interceptee
from dataentry.models import InterceptionRecord
from dataentry.models import UserLocationPermission
from dataentry.models import Country
from dataentry.models import Form
from dataentry.models import FormCategory
from rest_api.authentication_expansion import HasPermission, HasDeletePermission, HasPostPermission, HasPutPermission
from static_border_stations.models import BorderStation


class BudgetViewSet(viewsets.ModelViewSet):
    queryset = BorderStationBudgetCalculation.objects.all()
    serializer_class = BorderStationBudgetCalculationSerializer
    permission_classes = [IsAuthenticated, HasPermission, HasDeletePermission, HasPostPermission, HasPutPermission]
    permissions_required = [{'permission_group':'BUDGETS', 'action':'VIEW'},]
    delete_permissions_required = [{'permission_group':'BUDGETS', 'action':'DELETE'},]
    post_permissions_required = [{'permission_group':'BUDGETS', 'action':'ADD'},]
    put_permissions_required = [{'permission_group':'BUDGETS', 'action':'EDIT'},]
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ['border_station__station_name', 'border_station__station_code']
    ordering_fields = ['border_station__station_name', 'border_station__station_code', 'month_year', 'date_time_entered', 'date_time_last_updated']

    def or_qfilter(self, qfilter, element):
        if qfilter == None:
            qfilter = element
        else:
            qfilter = qfilter | element
        return qfilter
    
    def list(self, request, *args, **kwargs):
        in_country = self.request.GET.get('country_ids')
        countries = Country.objects.all()
        all_country_list = []
        for country in countries:
            all_country_list.append(country.id)
        
        country_list = []
        if in_country is not None and in_country != '':
            # client provided a list of countries to consider
            for cntry in in_country.split(','):
                country_list.append(int(cntry))
        else:
            # client did not provide a list - so consider all countries
           country_list = all_country_list
           
        ulps = UserLocationPermission.objects.filter(account__id = request.user.id, permission__permission_group = 'BUDGETS', permission__action='VIEW')
        qfilter = None
        for ulp in ulps:
            if ulp.country is None:
                if ulp.station is None:
                    if in_country is None:
                        qfilter = None
                    else:
                        for country_id in country_list:
                            qfilter = self.or_qfilter(qfilter, Q(border_station__operating_country__id = country_id))
                    break;
                elif ulp.station.operating_country.id in country_list:
                    qfilter = self.or_qfilter(qfilter, Q(border_station__id = ulp.station.id))
            elif ulp.country.id in country_list:
                qfilter = self.or_qfilter(qfilter, Q(border_station__operating_country__id = ulp.country.id))
        
        if qfilter is not None:
            self.queryset = self.queryset.filter(qfilter)               
            
        temp = self.serializer_class
        self.serializer_class = BorderStationBudgetCalculationListSerializer  # we want to use a custom serializer just for the list view
        super_list_response = super(BudgetViewSet, self).list(request, *args, **kwargs)  # call the supers list view with custom serializer
        self.serializer_class = temp  # put the original serializer back in place
        return super_list_response

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def budget_sheet_by_date(request, pk, month, year):
    form = {"border_station": int(pk)}
    other_items = []
    staff_items = []
    
    date = datetime.date(int(year), int(month), 1)
    budget_sheets = BorderStationBudgetCalculation.objects.filter(
        border_station=pk,
        month_year__lte=date
    ).order_by('-date_time_entered')

    if budget_sheets and len(budget_sheets) > 0:
        previous_budget_sheet = budget_sheets[0]
        other_items_serializer = OtherBudgetItemCostSerializer(previous_budget_sheet.otherbudgetitemcost_set.all(), many=True)
        staff_serializer = StaffBudgetItemSerializer(previous_budget_sheet.staffbudgetitem_set.all(), many=True)
        budget_serializer = BorderStationBudgetCalculationSerializer(previous_budget_sheet)

        staff_items = staff_serializer.data
        other_items = other_items_serializer.data
        form = budget_serializer.data

    return Response({
        'top_table_data': top_table_data(pk, month, year, budget_sheets),
        'form': form,
        'staff_items': staff_items,
        'other_items': other_items
    })



@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def get_top_table_data(request, pk):
    budget_sheet = BorderStationBudgetCalculation.objects.get(pk=pk)

    budget_sheets = BorderStationBudgetCalculation.objects.filter(
        border_station=budget_sheet.border_station,
        month_year__lt=budget_sheet.month_year
    ).order_by('-date_time_entered')

    return Response(top_table_data(budget_sheet.border_station.id, budget_sheet.month_year.month, budget_sheet.month_year.year, budget_sheets))


def top_table_data(pk, month, year, budget_sheets):
    date = datetime.datetime(int(year), int(month), 1)  # We pass the Month_year as two key-word arguments because the day is always 1
    border_station = BorderStation.objects.get(pk=pk)
    staff_count = border_station.staff_set.count()
    
    form = Form.current_form('IRF',border_station.id)
    form_categories = FormCategory.objects.filter(form=form, name='People')
    if len(form_categories) < 0 or form_categories[0].storage is None:
        return None
    
    form_class = form_categories[0].storage.get_form_storage_class()
    
    
    # Last month data will count records from the 1st of this month to end of this month by pulling data less than the first of next month
    all_interceptions = form_class.objects.filter(interception_record__irf_number__startswith=border_station.station_code, person__role='PVOT')

    last_months_count = all_interceptions.filter(
            interception_record__date_time_entered_into_system__gte=date,
            interception_record__date_time_entered_into_system__lt=date+relativedelta(months=1)).count()
    last_3_months_count = all_interceptions.filter(
            interception_record__date_time_entered_into_system__gte=date+relativedelta(months=-2),
            interception_record__date_time_entered_into_system__lt=date+relativedelta(months=1)).count()
    all_interception_records_count = all_interceptions.count()

    if budget_sheets:  # If this border station has had a previous budget calculation worksheet
        last_3_months_count_divide = last_3_months_count if last_3_months_count != 0 else 1
        last_months_count_divide = last_months_count if last_months_count != 0 else 1
        all_interception_records_count_divide = all_interception_records_count if all_interception_records_count != 0 else 1

        last_months_sheets = budget_sheets.filter(month_year__gte=date+relativedelta(months=-1))
        last_months_cost = last_months_sheets[0].station_total() if last_months_sheets.count() > 0 else 0

        last_3_months_cost = 0
        last_3_months_sheets = budget_sheets.filter(month_year__gte=date+relativedelta(months=-3))
        for sheet in last_3_months_sheets:
            last_3_months_cost += sheet.station_total()

        all_cost = 0
        for sheet in budget_sheets:
            all_cost += sheet.station_total()

        return {
                "all": all_interception_records_count,
                "all_cost": all_cost,
                "all_int_cost": all_cost/all_interception_records_count_divide,
                "last_month": last_months_count,
                "last_months_cost": last_months_cost,
                "last_months_int_cost": last_months_cost/last_months_count_divide,
                "last_3_months": last_3_months_count,
                "last_3_months_cost": last_3_months_cost,
                "last_3_months_int_cost": last_3_months_cost/last_3_months_count_divide,
                "staff_count": staff_count,
                "last_months_total_cost": last_months_cost
        }

    # If this border station has not had a previous budget calculation worksheet
    return {
         "all": all_interception_records_count,
         "all_cost": 0,
         "last_month": last_months_count,
         "last_months_cost": 0,
         "last_3_months": last_3_months_count,
         "last_3_months_cost": 0,
         "staff_count": staff_count,
         "last_months_total_cost": 0
    }


class OtherItemsViewSet(viewsets.ModelViewSet):
    queryset = OtherBudgetItemCost.objects.all()
    serializer_class = OtherBudgetItemCostSerializer
    permission_classes = [IsAuthenticated, HasPermission, HasDeletePermission, HasPostPermission, HasPutPermission]
    permissions_required = [{'permission_group':'BUDGETS', 'action':'VIEW'},]
    delete_permissions_required = [{'permission_group':'BUDGETS', 'action':'DELETE'},]
    post_permissions_required = [{'permission_group':'BUDGETS', 'action':'ADD'},]
    put_permissions_required = [{'permission_group':'BUDGETS', 'action':'EDIT'},]
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

class StaffBudgetItemViewSet(viewsets.ModelViewSet):
    queryset = StaffBudgetItem.objects.all()
    serializer_class = StaffBudgetItemSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    permissions_required = [{'permission_group':'BUDGETS', 'action':'VIEW'},]

    def budget_calc_retrieve(self, request, *args, **kwargs):
        """
            Retrieve all of the staffSalaries for a particular budget calculation sheet
        """
        self.object_list = self.filter_queryset(self.get_queryset().filter(budget_calc_sheet=self.kwargs['parent_pk']))
        serializer = self.get_serializer(self.object_list, many=True)
        return Response(serializer.data)
