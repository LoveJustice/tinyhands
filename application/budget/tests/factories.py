import datetime
import factory
import pytz

from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyInteger

from budget.models import BorderStationBudgetCalculation, OtherBudgetItemCost, StaffBudgetItem
from static_border_stations.tests.factories import BorderStationFactory, StaffFactory


class StaffBudgetItemFactory(DjangoModelFactory):
    class Meta:
        model = StaffBudgetItem

    cost = factory.fuzzy.FuzzyInteger(200, 800)
    type_name = 'Salary'
    staff_person = factory.SubFactory(StaffFactory)


class BorderStationBudgetCalculationFactory(DjangoModelFactory):
    class Meta:
        model = BorderStationBudgetCalculation

    mdf_uuid = "e788c527-7102-4e9c-a391-1b73653a03c5"

    border_station = factory.SubFactory(BorderStationFactory)
    month_year = datetime.datetime(2015, 5, 5, 5, tzinfo=pytz.UTC)

    communication_chair = True
    communication_chair_amount = FuzzyInteger(200, 800)

    travel_chair_with_bike = True
    travel_chair_with_bike_amount = FuzzyInteger(1800, 2200)
    travel_plus_other = FuzzyInteger(1000, 2000)

    administration_number_of_intercepts_last_month = FuzzyInteger(1, 4)
    administration_number_of_intercepts_last_month_multiplier = 20
    administration_number_of_intercepts_last_month_adder = FuzzyInteger(1000, 2000)
    administration_number_of_meetings_per_month = FuzzyInteger(1, 4)
    administration_number_of_meetings_per_month_multiplier = 600
    administration_booth = True
    administration_booth_amount = FuzzyInteger(1000, 3000)
    administration_office = True
    administration_office_amount = FuzzyInteger(1000, 3000)


    shelter_rent = True
    shelter_rent_amount = FuzzyInteger(200, 400)
    shelter_water = True
    shelter_water_amount = FuzzyInteger(200, 400)
    shelter_electricity = True
    shelter_electricity_amount = FuzzyInteger(200, 400)

    food_and_gas_number_of_intercepted_girls = FuzzyInteger(1, 4)
    food_and_gas_number_of_intercepted_girls_multiplier_before = 100
    food_and_gas_number_of_intercepted_girls_multiplier_after = 3
    food_and_gas_limbo_girls_multiplier = 100

    awareness_contact_cards = True
    awareness_contact_cards_boolean_amount = FuzzyInteger(1000, 4000)
    awareness_contact_cards_amount = FuzzyInteger(100, 300)
    awareness_awareness_party_boolean = True
    awareness_awareness_party = FuzzyInteger(300, 500)

    # members
    member1 = factory.RelatedFactory(StaffBudgetItemFactory, 'budget_calc_sheet')
    member2 = factory.RelatedFactory(StaffBudgetItemFactory, 'budget_calc_sheet')

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



