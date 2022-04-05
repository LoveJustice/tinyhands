import uuid
from datetime import datetime

from django.db import models

from dataentry.models import BorderStation
from static_border_stations.models import Staff


class BorderStationBudgetCalculation(models.Model):
    TRAVEL = 1
    MISCELLANEOUS = 2
    AWARENESS = 3
    POTENTIAL_VICTIM_CARE = 5
    COMMUNICATION = 7
    STAFF_BENEFITS = 8
    ADMINISTRATION = 10
    PAST_MONTH_SENT = 11
    LIMBO = 12
    MONEY_NOT_SPENT = 13
    IMPACT_MULTIPLYING = 14
    RENT_UTILITIES = 15

    mdf_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    date_time_entered = models.DateTimeField(auto_now_add=True)
    date_time_last_updated = models.DateTimeField(auto_now=True)

    month_year = models.DateTimeField(default=datetime.now)

    border_station = models.ForeignKey(BorderStation, on_delete=models.CASCADE)

    communication_chair = models.BooleanField(default=False)
    communication_chair_amount = models.DecimalField('for chair', max_digits=17, decimal_places=2, default=1000)

    def communication_extra_items_total(self):
        return self.other_items_total(self.COMMUNICATION)

    def communication_manager_chair_total(self):
        total = 0
        if self.communication_chair:
            total += self.communication_chair_amount
        return total

    def communication_total(self):
        total = 0
        total += self.communication_manager_chair_total()
        total += self.communication_extra_items_total()
        total += self.staff_items_total('Communication')
        return total

    travel_chair = models.BooleanField(default=False)
    travel_chair_amount = models.DecimalField('for chair (if has bike)', max_digits=17, decimal_places=2, default=2000)

    def travel_extra_items_total(self):
        return self.other_items_total(self.TRAVEL)

    def travel_manager_chair_total(self):
        total = 0
        if self.travel_chair:
            total += self.travel_chair_amount
        return total

    def travel_total(self):
        total = 0
        total += self.travel_extra_items_total()
        total += self.travel_manager_chair_total()
        total += self.staff_items_total('Travel')
        return total

    number_of_intercepts_last_month = models.PositiveIntegerField('# of intercepts last month', default=0)
    number_of_intercepts_last_month_multiplier = models.DecimalField(max_digits=17, decimal_places=2, default=20)
    number_of_intercepts_last_month_adder = models.DecimalField(max_digits=17, decimal_places=2, default=1000)
    number_of_meetings_per_month = models.PositiveIntegerField('# of meetings per month', default=0)
    number_of_meetings_per_month_multiplier = models.DecimalField(max_digits=17, decimal_places=2, default=600)
    booth = models.BooleanField('Booth', default=False)
    booth_amount = models.DecimalField(max_digits=17, decimal_places=2, default=30000)
    office = models.BooleanField('Office', default=False)
    office_amount = models.DecimalField(max_digits=17, decimal_places=2, default=2000)

    def administration_intercepts_total(self):
        return self.number_of_intercepts_last_month * self.number_of_intercepts_last_month_multiplier + self.number_of_intercepts_last_month_adder

    def administration_meetings_total(self):
        return self.number_of_meetings_per_month * self.number_of_meetings_per_month_multiplier

    def administration_extra_items_total(self):
        return self.other_items_total(self.ADMINISTRATION)

    def administration_total(self):
        total = 0
        total += self.administration_intercepts_total()
        total += self.administration_meetings_total()
        if self.booth:
            total += self.booth_amount
        if self.office:
            total += self.office_amount
        return total + self.administration_extra_items_total()

    def miscellaneous_total(self):
        return self.other_items_total(self.MISCELLANEOUS)
    
    def past_month_sent_total(self):
        return self.other_items_total(self.PAST_MONTH_SENT)
    
    shelter_rent = models.BooleanField('Rent', default=False)
    shelter_rent_amount = models.DecimalField(max_digits=17, decimal_places=2, default=0)
    shelter_water = models.BooleanField('Water', default=False)
    shelter_water_amount = models.DecimalField(max_digits=17, decimal_places=2, default=0)
    shelter_electricity = models.BooleanField('Electricity', default=False)
    shelter_electricity_amount = models.DecimalField(max_digits=17, decimal_places=2, default=0)

    def shelter_total(self):
        total = 0
        if self.shelter_rent:
            total += self.shelter_rent_amount
        if self.shelter_water:
            total += self.shelter_water_amount
        if self.shelter_electricity:
            total += self.shelter_electricity_amount
        return total
    
    def pv_extra_items_total(self):
        return self.other_items_total(self.POTENTIAL_VICTIM_CARE)
    
    def pv_total(self):
        return self.shelter_total() + self.food_and_gas_total() + self.pv_extra_items_total()

    number_of_intercepted_pvs = models.PositiveIntegerField('# of intercepted girls', default=0)
    food_per_pv_amount = models.DecimalField(max_digits=17, decimal_places=2, default=100)
    number_of_pv_days = models.PositiveIntegerField(default=3)
    limbo_girls_multiplier = models.DecimalField(max_digits=17, decimal_places=2, default=100)

    def food_and_gas_intercepted_girls_total(self):
        return self.number_of_intercepted_pvs * self.food_per_pv_amount * self.number_of_pv_days

    def food_and_gas_limbo_girls_total(self):
        return self.limbo_girls_multiplier * self.other_items_total(self.LIMBO)

    def food_and_gas_total(self):
        total = 0
        total += self.food_and_gas_intercepted_girls_total()
        total += self.food_and_gas_limbo_girls_total()
        return total

    contact_cards = models.BooleanField('Contact Cards', default=False)
    contact_cards_amount = models.DecimalField(max_digits=17, decimal_places=2, default=0)
    awareness_party_boolean = models.BooleanField("Awareness Party", default=False)
    awareness_party = models.DecimalField(max_digits=17, decimal_places=2, default=0)

    def awareness_extra_items_total(self):
        return self.other_items_total(self.AWARENESS)

    def awareness_total(self):
        total = self.awareness_extra_items_total()
        if self.contact_cards:
            total += self.contact_cards_amount
        if self.awareness_party_boolean:
            total += self.awareness_party
        return total

    def salary_total(self):
        total = sum([staff.cost for staff in self.staffbudgetitem_set.exclude(cost__isnull=True).exclude(
                type_name='Communication').exclude(type_name='Travel').exclude(type_name='Deductions')])
        total -= sum([staff.cost for staff in self.staffbudgetitem_set.filter(type_name='Deductions').exclude(cost__isnull=True)])
        return total
    
    def staff_and_benefits_total(self):
        return self.salary_total() + self.other_items_total(self.STAFF_BENEFITS)
    
    def money_not_spent_to_deduct(self):
        items = self.otherbudgetitemcost_set.filter(form_section=self.MONEY_NOT_SPENT, deduct='Yes').exclude(cost__isnull=True)
        return sum(item.cost for item in items)

    def station_total(self):
        total = 0
        total += self.staff_and_benefits_total()
        total += self.awareness_total()
        total += self.pv_total()
        total += self.communication_total()
        total += self.administration_total()
        total += self.miscellaneous_total()
        total += self.travel_total()
        total -= self.money_not_spent_to_deduct()
        return total
    
    notes = models.TextField('Notes', blank=True)

    def other_items_total(self, section):
        items = self.otherbudgetitemcost_set.filter(form_section=section).exclude(cost__isnull=True)
        return sum(item.cost for item in items)
    
    def staff_items_total(self, the_type):
        items = self.staffbudgetitem_set.filter(type_name=the_type).exclude(cost__isnull=True)
        return sum(item.cost for item in items)

    def mdf_file_name(self):
        return '{}-{}-{}-MDF.pdf'.format(self.border_station.station_code, self.month_year.month, self.month_year.year)

    def get_country_id(self):
        if self.border_station is None or self.border_station.operating_country is None:
            return None
        return self.border_station.operating_country.id  
    
    def get_border_station_id(self):
        if self.border_station is None:
            return None
        return self.border_station.id
    
    def __str__(self):
        return "{} - {}".format(self.border_station.station_name, self.month_year)


class OtherBudgetItemCost(models.Model):

    BUDGET_FORM_SECTION_CHOICES = [
        (BorderStationBudgetCalculation.TRAVEL, 'Travel'),
        (BorderStationBudgetCalculation.MISCELLANEOUS, 'Miscellaneous'),
        (BorderStationBudgetCalculation.AWARENESS, 'Awareness'),
        (BorderStationBudgetCalculation.POTENTIAL_VICTIM_CARE, 'Potential Victim Care'),
        (BorderStationBudgetCalculation.COMMUNICATION, 'Communication'),
        (BorderStationBudgetCalculation.STAFF_BENEFITS, 'Staff & Benefits'),
        (BorderStationBudgetCalculation.ADMINISTRATION, 'Administration'),
        (BorderStationBudgetCalculation.PAST_MONTH_SENT, 'Past Month Sent Money'),
        (BorderStationBudgetCalculation.LIMBO, 'Limbo Potential Victims'),
        (BorderStationBudgetCalculation.MONEY_NOT_SPENT, 'Money Not Spent')
    ]
    name = models.CharField(max_length=255, blank=False)
    cost = models.DecimalField(max_digits=17, decimal_places=2, default=0, blank=False)
    form_section = models.IntegerField(BUDGET_FORM_SECTION_CHOICES, blank=True, null=True)
    budget_item_parent = models.ForeignKey(BorderStationBudgetCalculation, blank=True, null=True, on_delete=models.CASCADE)
    associated_section = models.IntegerField(BUDGET_FORM_SECTION_CHOICES, blank=True, null=True)
    deduct = models.CharField(max_length=255, blank=True, null=True)
    work_project = models.ForeignKey(BorderStation, null=True)
    
    def get_country_id(self):
        if self.budget_item_parent is None or self.budget_item_parent.border_station is None or self.budget_item_parent.border_station.operating_country is None:
            return None
        return self.budget_item_parent.border_station.operating_country.id  
    
    def get_border_station_id(self):
        if self.budget_item_parent is None or self.budget_item_parent.border_station is None:
            return None
        return self.budget_item_parent.border_station.id


class StaffBudgetItem(models.Model):
    budget_calc_sheet = models.ForeignKey(BorderStationBudgetCalculation, blank=True, null=True, on_delete=models.CASCADE)
    staff_person = models.ForeignKey(Staff, blank=True, null=True, on_delete=models.CASCADE)
    type_name = models.CharField(max_length=255, blank=False)
    description = models.TextField('Description', blank=True)
    cost = models.DecimalField(max_digits=17, decimal_places=2, default=0, blank=True, null=True)
    work_project = models.ForeignKey(BorderStation, null=True)
    
    def get_country_id(self):
        if self.budget_calc_sheet is None or self.budget_calc_sheet.border_station is None or self.budget_calc_sheet.border_station.operating_country is None:
            return None
        return self.budget_calc_sheet.border_station.operating_country.id  
    
    def get_border_station_id(self):
        if self.budget_calc_sheet is None or self.budget_calc_sheet.border_station is None:
            return None
        return self.budget_calc_sheet.border_station.id

    
    
    

