from datetime import datetime

from django.db import models

from dataentry.models import BorderStation
from static_border_stations.models import Staff


class BorderStationBudgetCalculation(models.Model):
    date_time_entered = models.DateTimeField(auto_now_add=True)
    date_time_last_updated = models.DateTimeField(auto_now=True)

    month_year = models.DateTimeField(default=datetime.now())

    border_station = models.ForeignKey(BorderStation)

    communication_chair = models.BooleanField(default=False)
    communication_chair_amount = models.PositiveIntegerField('for chair', default=1000)
    communication_manager = models.BooleanField(default=False)
    communication_manager_amount = models.PositiveIntegerField('for manager', default=1000)
    communication_number_of_staff_with_walkie_talkies = models.PositiveIntegerField('# of staff with walkie-talkies', default=0)
    communication_number_of_staff_with_walkie_talkies_multiplier = models.PositiveIntegerField(default=100)
    communication_each_staff = models.PositiveIntegerField('each staff', default=0)
    communication_each_staff_multiplier = models.PositiveIntegerField(default=300)

    def communication_total(self):
        total = 0
        if self.communication_chair:
            total += self.communication_chair_amount
        if self.communication_manager:
            total += self.communication_manager_amount
        total += self.communication_number_of_staff_with_walkie_talkies * self.communication_number_of_staff_with_walkie_talkies_multiplier
        total += self.communication_each_staff * self.communication_each_staff_multiplier
        return total

    travel_chair_with_bike = models.BooleanField(default=False)
    travel_chair_with_bike_amount = models.PositiveIntegerField('for chair (if has bike)', default=2000)
    travel_manager_with_bike = models.BooleanField(default=False)
    travel_manager_with_bike_amount = models.PositiveIntegerField('for manager (if has bike)', default=2000)
    travel_number_of_staff_using_bikes = models.PositiveIntegerField('# of staff using bikes', default=0)
    travel_number_of_staff_using_bikes_multiplier = models.PositiveIntegerField(default=1000)
    travel_last_months_expense_for_sending_girls_home = models.PositiveIntegerField(default=0)
    travel_motorbike = models.BooleanField('Motorbike', default=False)
    travel_motorbike_amount = models.PositiveIntegerField(default=60000)
    travel_plus_other = models.PositiveIntegerField(default=0)

    def travel_total(self):
        total = 0
        if self.travel_chair_with_bike:
            total += self.travel_chair_with_bike_amount
        if self.travel_manager_with_bike:
            total += self.travel_manager_with_bike_amount
        total += self.travel_number_of_staff_using_bikes * self.travel_number_of_staff_using_bikes_multiplier
        total += self.travel_last_months_expense_for_sending_girls_home
        if self.travel_motorbike:
            total += self.travel_motorbike_amount
        total += self.travel_plus_other
        return total

    administration_number_of_intercepts_last_month = models.PositiveIntegerField('# of intercepts last month', default=0)
    administration_number_of_intercepts_last_month_multiplier = models.PositiveIntegerField(default=20)
    administration_number_of_intercepts_last_month_adder = models.PositiveIntegerField(default=1000)
    administration_number_of_meetings_per_month = models.PositiveIntegerField('# of meetings per month', default=0)
    administration_number_of_meetings_per_month_multiplier = models.PositiveIntegerField(default=600)
    administration_booth = models.BooleanField('Booth', default=False)
    administration_booth_amount = models.PositiveIntegerField(default=30000)
    administration_registration = models.BooleanField('Registration', default=False)
    administration_registration_amount = models.PositiveIntegerField(default=2000)

    def administration_total(self):
        total = 0
        total += (self.administration_number_of_intercepts_last_month * self.administration_number_of_intercepts_last_month_multiplier) + self.administration_number_of_intercepts_last_month_adder
        total += self.administration_number_of_meetings_per_month * self.administration_number_of_meetings_per_month_multiplier
        if self.administration_booth:
            total += self.administration_booth_amount
        if self.administration_registration:
            total += self.administration_registration_amount
        return total

    medical_last_months_expense = models.PositiveIntegerField("Last month's medical expense", default=0)

    def medical_total(self):
        return self.medical_last_months_expense

    miscellaneous_number_of_intercepts_last_month = models.PositiveIntegerField('# of intercepts last month', default=0)
    miscellaneous_number_of_intercepts_last_month_multiplier = models.PositiveIntegerField(default=300)

    def miscellaneous_total(self):
        total = 0
        total += self.miscellaneous_number_of_intercepts_last_month * self.miscellaneous_number_of_intercepts_last_month_multiplier
        return total

    shelter_rent = models.PositiveIntegerField(default=0)
    shelter_water = models.PositiveIntegerField(default=0)
    shelter_electricity = models.PositiveIntegerField(default=0)
    shelter_shelter_startup = models.BooleanField('Shelter Startup', default=False)
    shelter_shelter_startup_amount = models.PositiveIntegerField(default=71800)
    shelter_shelter_two = models.BooleanField('Shelter 2', default=False)
    shelter_shelter_two_amount = models.PositiveIntegerField(default=36800)

    def shelter_total(self):
        total = 0
        total += self.shelter_rent + self.shelter_electricity + self.shelter_water
        if self.shelter_shelter_startup:
            total += self.shelter_shelter_startup_amount
        if self.shelter_shelter_two:
            total += self.shelter_shelter_two_amount
        return total

    food_and_gas_number_of_intercepted_girls = models.PositiveIntegerField('# of intercepted girls', default=0)
    food_and_gas_number_of_intercepted_girls_multiplier_before = models.PositiveIntegerField(default=100)
    food_and_gas_number_of_intercepted_girls_multiplier_after = models.PositiveIntegerField(default=3)
    food_and_gas_limbo_girls_multiplier = models.PositiveIntegerField(default=100)
    food_and_gas_number_of_limbo_girls = models.PositiveIntegerField('# of limbo girls', default=0)
    food_and_gas_number_of_days = models.PositiveIntegerField('# of days', default=0)

    def food_and_gas_total(self):
        total = 0
        total += (self.food_and_gas_number_of_intercepted_girls * self.food_and_gas_number_of_intercepted_girls_multiplier_before * self.food_and_gas_number_of_intercepted_girls_multiplier_after)
        total += (self.food_and_gas_limbo_girls_multiplier * self.food_and_gas_number_of_limbo_girls * self.food_and_gas_number_of_days)
        return total

    awareness_contact_cards = models.BooleanField('Contact Cards', default=False)
    awareness_contact_cards_boolean_amount = models.PositiveIntegerField(default=4000)
    awareness_contact_cards_amount = models.PositiveIntegerField(default=0)
    awareness_awareness_party_boolean = models.BooleanField("Awareness Party", default=False)
    awareness_awareness_party = models.PositiveIntegerField(default=0)
    awareness_sign_boards_boolean = models.BooleanField("Sign Boards", default=False)
    awareness_sign_boards = models.PositiveIntegerField(default=0)

    def awareness_total(self):
        total = 0
        # If test fails, check names of contact cards.
        if self.awareness_contact_cards:
            total += (self.awareness_contact_cards_amount + self.awareness_contact_cards_boolean_amount)
        if self.awareness_awareness_party_boolean:
            total += self.awareness_awareness_party
        if self.awareness_sign_boards_boolean:
            total += self.awareness_sign_boards
        return total

    supplies_walkie_talkies_boolean = models.BooleanField('Walkie-talkies', default=False)
    supplies_walkie_talkies_amount = models.PositiveIntegerField(default=0)
    supplies_recorders_boolean = models.BooleanField('Recorders', default=False)
    supplies_recorders_amount = models.PositiveIntegerField(default=0)
    supplies_binoculars_boolean = models.BooleanField('Binoculars', default=False)
    supplies_binoculars_amount = models.PositiveIntegerField(default=0)
    supplies_flashlights_boolean = models.BooleanField('Flashlights', default=False)
    supplies_flashlights_amount = models.PositiveIntegerField(default=0)

    def supplies_total(self):
        total = 0
        if self.supplies_walkie_talkies_boolean:
            total += self.supplies_walkie_talkies_amount
        if self.supplies_recorders_boolean:
            total += self.supplies_recorders_amount
        if self.supplies_binoculars_boolean:
            total += self.supplies_binoculars_amount
        if self.supplies_flashlights_boolean:
            total += self.supplies_flashlights_amount
        return total

    def station_total(self):
        total = 0
        total += self.supplies_total()
        total += self.awareness_total()
        total += self.food_and_gas_total()
        total += self.communication_total()
        total += self.medical_total()
        total += self.administration_total()
        total += self.miscellaneous_total()
        total += self.shelter_total()
        total += self.travel_total()
        return total

    members = models.ManyToManyField(Staff, through='StaffSalary')


class OtherBudgetItemCost(models.Model):
    name = models.CharField(max_length=255, blank=False)
    cost = models.PositiveIntegerField(default=0, blank=False)

    BUDGET_FORM_SECTION_CHOICES = [(1, 'Travel'), (2, 'Miscellaneous'), (3, 'Awareness'), (4, 'Supplies'), ]
    form_section = models.IntegerField(BUDGET_FORM_SECTION_CHOICES, blank=True, null=True)
    budget_item_parent = models.ForeignKey(BorderStationBudgetCalculation, blank=True, null=True)


class StaffSalary(models.Model):
    salary = models.PositiveIntegerField(default=0, blank=True, null=True)

    budget_calc_sheet = models.ForeignKey(BorderStationBudgetCalculation, blank=True, null=True)
    staff_person = models.ForeignKey(Staff, blank=True, null=True)
