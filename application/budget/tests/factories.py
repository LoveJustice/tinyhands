import datetime
import factory
import pytz

from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyInteger

from budget.models import BorderStationBudgetCalculation, OtherBudgetItemCost, StaffSalary
from static_border_stations.tests.factories import BorderStationFactory, StaffFactory


class StaffSalaryFactory(DjangoModelFactory):
    class Meta:
        model = StaffSalary

    salary = factory.fuzzy.FuzzyInteger(200, 800)
    staff_person = factory.SubFactory(StaffFactory)


class BorderStationBudgetCalculationFactory(DjangoModelFactory):
    class Meta:
        model = BorderStationBudgetCalculation

    border_station = factory.SubFactory(BorderStationFactory)
    month_year = datetime.datetime(2015, 5, 5, 5, tzinfo=pytz.UTC)

    communication_chair = True
    communication_chair_amount = FuzzyInteger(200, 800)
    communication_manager = True
    communication_manager_amount = FuzzyInteger(200, 800)
    communication_number_of_staff_with_walkie_talkies = FuzzyInteger(1, 4)
    communication_number_of_staff_with_walkie_talkies_multiplier = 100
    communication_each_staff = FuzzyInteger(1, 4)
    communication_each_staff_multiplier = 300

    travel_chair_with_bike = True
    travel_chair_with_bike_amount = FuzzyInteger(1800, 2200)
    travel_manager_with_bike = True
    travel_manager_with_bike_amount = FuzzyInteger(1800, 2200)
    travel_number_of_staff_using_bikes = FuzzyInteger(1, 4)
    travel_number_of_staff_using_bikes_multiplier = 1000
    travel_last_months_expense_for_sending_girls_home = FuzzyInteger(100, 220)
    travel_motorbike = True
    travel_motorbike_amount = FuzzyInteger(2000, 3000)
    travel_plus_other = FuzzyInteger(1000, 2000)

    administration_number_of_intercepts_last_month = FuzzyInteger(1, 4)
    administration_number_of_intercepts_last_month_multiplier = 20
    administration_number_of_intercepts_last_month_adder = FuzzyInteger(1000, 2000)
    administration_number_of_meetings_per_month = FuzzyInteger(1, 4)
    administration_number_of_meetings_per_month_multiplier = 600
    administration_booth = True
    administration_booth_amount = FuzzyInteger(1000, 3000)
    administration_registration = True
    administration_registration_amount = FuzzyInteger(1000, 3000)

    medical_last_months_expense = FuzzyInteger(1000, 3000)


    shelter_rent = FuzzyInteger(200, 400)
    shelter_water = FuzzyInteger(200, 400)
    shelter_electricity = FuzzyInteger(200, 400)
    shelter_shelter_startup = True
    shelter_shelter_startup_amount = FuzzyInteger(200, 400)
    shelter_shelter_two = True
    shelter_shelter_two_amount = FuzzyInteger(200, 400)

    food_and_gas_number_of_intercepted_girls = FuzzyInteger(1, 4)
    food_and_gas_number_of_intercepted_girls_multiplier_before = 100
    food_and_gas_number_of_intercepted_girls_multiplier_after = 3
    food_and_gas_limbo_girls_multiplier = 100
    food_and_gas_number_of_limbo_girls = FuzzyInteger(1, 4)
    food_and_gas_number_of_days = FuzzyInteger(1, 7)

    awareness_contact_cards = True
    awareness_contact_cards_boolean_amount = FuzzyInteger(1000, 4000)
    awareness_contact_cards_amount = FuzzyInteger(100, 300)
    awareness_awareness_party_boolean = True
    awareness_awareness_party = FuzzyInteger(300, 500)
    awareness_sign_boards_boolean = True
    awareness_sign_boards = FuzzyInteger(200, 400)

    supplies_walkie_talkies_boolean = True
    supplies_walkie_talkies_amount = FuzzyInteger(200, 400)
    supplies_recorders_boolean = True
    supplies_recorders_amount = FuzzyInteger(200, 400)
    supplies_binoculars_boolean = True
    supplies_binoculars_amount = FuzzyInteger(200, 400)
    supplies_flashlights_boolean = True
    supplies_flashlights_amount = FuzzyInteger(200, 400)

    # members
    member1 = factory.RelatedFactory(StaffSalaryFactory, 'budget_calc_sheet')
    member2 = factory.RelatedFactory(StaffSalaryFactory, 'budget_calc_sheet')

    @factory.post_generation
    def post(self, created, extracted, **kwargs):
        for section in [x[0] for x in OtherBudgetItemCost.BUDGET_FORM_SECTION_CHOICES]:
            OtherBudgetItemCostFactory(form_section=section, budget_item_parent=self)


class OtherBudgetItemCostFactory(DjangoModelFactory):
    class Meta:
        model = OtherBudgetItemCost

    name = factory.Sequence(lambda n: 'Other Item #{0}'.format(n))
    cost = FuzzyInteger(100, 500)
    form_section = factory.Iterator(OtherBudgetItemCost.BUDGET_FORM_SECTION_CHOICES, getter=lambda c: c[0])
    budget_item_parent = factory.SubFactory(BorderStationBudgetCalculationFactory)



