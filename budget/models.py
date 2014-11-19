from django.db import models
from accounts.models import Account
from dataentry.models import BorderStation


class BorderStationBudgetCalculation(models.Model):
    form_entered_by = models.ForeignKey(Account, related_name="form_entered_by_account")
    form_updated_by = models.ForeignKey(Account, related_name="form_updated_by_account")

    date_time_entered = models.DateTimeField(auto_now_add=True)
    date_time_last_updated = models.DateTimeField(auto_now=True)

    border_station = models.ForeignKey(BorderStation)

    communication_chair = models.BooleanField(default=False)
    communication_chair_amount = models.PositiveIntegerField('for chair', default=1000)
    communication_manager = models.BooleanField(default=False)
    communication_manager_amount = models.PositiveIntegerField('for manager (if station has manager)', default=1000)
    communication_number_of_staff_with_walkie_talkies = models.PositiveIntegerField('# of staff with walkie-talkies', default=0)
    communication_number_of_staff_with_walkie_talkies_multiplier = models.PositiveIntegerField(default=100)
    communication_each_staff = models.PositiveIntegerField('each staff', default=0)
    communication_each_staff_multiplier = models.PositiveIntegerField(default=300)


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


    administration_number_of_intercepts_last_month = models.PositiveIntegerField('# of intercepts last month', default=0)
    administration_number_of_intercepts_last_month_multiplier = models.PositiveIntegerField(default=20)
    administration_number_of_intercepts_last_month_adder = models.PositiveIntegerField(default=1000)
    administration_number_of_meetings_per_month = models.PositiveIntegerField('# of meetings per month', default=0)
    administration_number_of_meetings_per_month_multiplier = models.PositiveIntegerField(default=600)
    administration_booth = models.BooleanField('Booth', default=False)
    administration_booth_amount = models.PositiveIntegerField(default=30000)
    administration_registration = models.BooleanField('Registration', default=False)
    administration_registration_amount = models.PositiveIntegerField(default=2000)


    medical_last_months_expense = models.PositiveIntegerField("Last month's medical expense", default=0)


    miscellaneous_number_of_intercepts_last_month = models.PositiveIntegerField('# of intercepts last month', default=0)
    miscellaneous_number_of_intercepts_last_month_multiplier = models.PositiveIntegerField(default=300)


    shelter_rent = models.PositiveIntegerField(default=0)
    shelter_water = models.PositiveIntegerField(default=0)
    shelter_electricity = models.PositiveIntegerField(default=0)
    shelter_shelter_startup = models.BooleanField('Shelter Startup', default=False)
    shelter_shelter_startup_amount = models.PositiveIntegerField(default=71800)
    shelter_shelter_two = models.BooleanField('Shelter 2', default=False)
    shelter_shelter_two_amount = models.PositiveIntegerField(default=36800)


    food_and_gas_number_of_intercepted_girls = models.PositiveIntegerField('# of intercepted girls', default=0)
    food_and_gas_number_of_intercepted_girls_multiplier_before = models.PositiveIntegerField(default=100)
    food_and_gas_number_of_intercepted_girls_multiplier_after = models.PositiveIntegerField(default=3)
    food_and_gas_limbo_girls_multiplier = models.PositiveIntegerField(default=100)
    food_and_gas_number_of_limbo_girls = models.PositiveIntegerField('# of limbo girls', default=0)
    food_and_gas_number_of_days = models.PositiveIntegerField('# of days', default=0)


    awareness_contact_cards = models.BooleanField('Contact Cards', default=False)
    awareness_contact_cards_boolean_amount = models.PositiveIntegerField(default=4000)
    awareness_contact_cards_amount = models.PositiveIntegerField(default=0)
    awareness_awareness_party_boolean = models.BooleanField("Awareness Party", default=False)
    awareness_awareness_party = models.PositiveIntegerField(default=0)
    awareness_sign_boards_boolean = models.BooleanField("Sign Boards", default=False)
    awareness_sign_boards = models.PositiveIntegerField(default=0)


    supplies_walkie_talkies_boolean = models.BooleanField('Walkie-talkies', default=False)
    supplies_walkie_talkies_amount = models.PositiveIntegerField(default=0)
    supplies_recorders_boolean = models.BooleanField('Recorders', default=False)
    supplies_recorders_amount = models.PositiveIntegerField(default=0)
    supplies_binoculars_boolean = models.BooleanField('Binoculars', default=False)
    supplies_binoculars_amount = models.PositiveIntegerField(default=0)
    supplies_flashlights_boolean = models.BooleanField('Flashlights', default=False)
    supplies_flashlights_amount = models.PositiveIntegerField(default=0)


class OtherBudgetItemCost(models.Model):
    name = models.CharField(max_length=255)
    cost = models.PositiveIntegerField()

    BUDGET_FORM_SECTION_CHOICES = [
        (1, 'Travel'),
        (2, 'Miscellaneous'),
        (3, 'Awareness'),
        (4, 'Supplies'),
    ]
    form_section = models.IntegerField(BUDGET_FORM_SECTION_CHOICES)
    budget_item_parent = models.ForeignKey(BorderStationBudgetCalculation)
