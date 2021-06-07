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

    mdf_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    date_time_entered = models.DateTimeField(auto_now_add=True)
    date_time_last_updated = models.DateTimeField(auto_now=True)

    month_year = models.DateTimeField(default=datetime.now)

    border_station = models.ForeignKey(BorderStation, on_delete=models.CASCADE)

    communication_chair = models.BooleanField(default=False)
    communication_chair_amount = models.PositiveIntegerField('for chair', default=1000)

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

    travel_chair_with_bike = models.BooleanField(default=False)
    travel_chair_with_bike_amount = models.PositiveIntegerField('for chair (if has bike)', default=2000)
    travel_plus_other = models.PositiveIntegerField(default=0)

    def travel_extra_items_total(self):
        return self.other_items_total(self.TRAVEL)

    def travel_manager_chair_total(self):
        total = 0
        if self.travel_chair_with_bike:
            total += self.travel_chair_with_bike_amount
        return total

    def travel_total(self):
        total = 0
        total += self.travel_extra_items_total()
        total += self.travel_manager_chair_total()
        total += self.staff_items_total('Travel')
        total += self.travel_plus_other
        return total

    administration_number_of_intercepts_last_month = models.PositiveIntegerField('# of intercepts last month', default=0)
    administration_number_of_intercepts_last_month_multiplier = models.PositiveIntegerField(default=20)
    administration_number_of_intercepts_last_month_adder = models.PositiveIntegerField(default=1000)
    administration_number_of_meetings_per_month = models.PositiveIntegerField('# of meetings per month', default=0)
    administration_number_of_meetings_per_month_multiplier = models.PositiveIntegerField(default=600)
    administration_booth = models.BooleanField('Booth', default=False)
    administration_booth_amount = models.PositiveIntegerField(default=30000)
    administration_office = models.BooleanField('Office', default=False)
    administration_office_amount = models.PositiveIntegerField(default=2000)

    def administration_intercepts_total(self):
        return self.administration_number_of_intercepts_last_month * self.administration_number_of_intercepts_last_month_multiplier + self.administration_number_of_intercepts_last_month_adder

    def administration_meetings_total(self):
        return self.administration_number_of_meetings_per_month * self.administration_number_of_meetings_per_month_multiplier

    def administration_extra_items_total(self):
        return self.other_items_total(self.ADMINISTRATION)

    def administration_total(self):
        total = 0
        total += self.administration_intercepts_total()
        total += self.administration_meetings_total()
        if self.administration_booth:
            total += self.administration_booth_amount
        if self.administration_office:
            total += self.administration_office_amount
        return total + self.administration_extra_items_total()

    def miscellaneous_total(self):
        return self.other_items_total(self.MISCELLANEOUS)
    
    def past_month_sent_total(self):
        return self.other_items_total(self.PAST_MONTH_SENT)
    
    shelter_rent = models.BooleanField('Rent', default=False)
    shelter_rent_amount = models.PositiveIntegerField(default=0)
    shelter_water = models.BooleanField('Water', default=False)
    shelter_water_amount = models.PositiveIntegerField(default=0)
    shelter_electricity = models.BooleanField('Electricity', default=False)
    shelter_electricity_amount = models.PositiveIntegerField(default=0)

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

    food_and_gas_number_of_intercepted_girls = models.PositiveIntegerField('# of intercepted girls', default=0)
    food_and_gas_number_of_intercepted_girls_multiplier_before = models.PositiveIntegerField(default=100)
    food_and_gas_number_of_intercepted_girls_multiplier_after = models.PositiveIntegerField(default=3)
    food_and_gas_limbo_girls_multiplier = models.PositiveIntegerField(default=100)
    food_and_gas_number_of_limbo_girls = models.PositiveIntegerField('# of limbo girls', default=0)
    food_and_gas_number_of_days = models.PositiveIntegerField('# of days', default=0)

    def food_and_gas_intercepted_girls_total(self):
        return self.food_and_gas_number_of_intercepted_girls * self.food_and_gas_number_of_intercepted_girls_multiplier_before * self.food_and_gas_number_of_intercepted_girls_multiplier_after

    def food_and_gas_limbo_girls_total(self):
        return self.food_and_gas_limbo_girls_multiplier * self.food_and_gas_number_of_limbo_girls * self.food_and_gas_number_of_days

    def food_and_gas_total(self):
        total = 0
        total += self.food_and_gas_intercepted_girls_total()
        total += self.food_and_gas_limbo_girls_total()
        return total

    awareness_contact_cards = models.BooleanField('Contact Cards', default=False)
    awareness_contact_cards_boolean_amount = models.PositiveIntegerField(default=4000)
    awareness_contact_cards_amount = models.PositiveIntegerField(default=0)
    awareness_awareness_party_boolean = models.BooleanField("Awareness Party", default=False)
    awareness_awareness_party = models.PositiveIntegerField(default=0)
    awareness_sign_boards_boolean = models.BooleanField("Sign Boards", default=False)
    awareness_sign_boards = models.PositiveIntegerField(default=0)

    def awareness_extra_items_total(self):
        return self.other_items_total(self.AWARENESS)

    def awareness_total(self):
        total = self.awareness_extra_items_total()
        if self.awareness_contact_cards:
            total += self.awareness_contact_cards_amount
        if self.awareness_awareness_party_boolean:
            total += self.awareness_awareness_party
        if self.awareness_sign_boards_boolean:
            total += self.awareness_sign_boards
        return total

    def salary_total(self):
        return sum([staff.cost for staff in self.staffbudgetitem_set.exclude(cost__isnull=True).exclude(type_name='Communication').exclude(type_name='Travel')])
    
    def staff_and_benefits_total(self):
        return self.salary_total() + self.other_items_total(self.STAFF_BENEFITS)

    def station_total(self):
        total = 0
        total += self.staff_and_benefits_total()
        total += self.awareness_total()
        total += self.pv_total()
        total += self.communication_total()
        total += self.administration_total()
        total += self.miscellaneous_total()
        total += self.travel_total()
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
        (BorderStationBudgetCalculation.PAST_MONTH_SENT, 'Past Month Sent Money')
    ]
    name = models.CharField(max_length=255, blank=False)
    cost = models.IntegerField(default=0, blank=False)
    form_section = models.IntegerField(BUDGET_FORM_SECTION_CHOICES, blank=True, null=True)
    budget_item_parent = models.ForeignKey(BorderStationBudgetCalculation, blank=True, null=True, on_delete=models.CASCADE)
    
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
    cost = models.IntegerField(default=0, blank=True, null=True)
    
    def get_country_id(self):
        if self.budget_calc_sheet is None or self.budget_calc_sheet.border_station is None or self.budget_calc_sheet.border_station.operating_country is None:
            return None
        return self.budget_calc_sheet.border_station.operating_country.id  
    
    def get_border_station_id(self):
        if self.budget_calc_sheet is None or self.budget_calc_sheet.border_station is None:
            return None
        return self.budget_calc_sheet.border_station.id
    
    

