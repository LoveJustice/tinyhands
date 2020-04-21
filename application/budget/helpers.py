from collections import namedtuple

from time import strftime

from budget.models import BorderStationBudgetCalculation

BudgetLineItem = namedtuple('budgetItem', ['name', 'value'])


class BudgetTable:
    ROW_HEIGHT = 18
    TITLE_HEIGHT = 36
    NAME_LENGTH = 29

    def __init__(self, title, items):
        self.title = title
        self.items = items

    @property
    def total(self):
        return sum([item.value for item in self.items])

    @property
    def height_required(self):
        # for helping calculate the height required to render the table
        # using points where 1 point = 1/72 of an inch
        # not the greatest but hopefully future devs will find a better way - AS
        row_count = sum([(len(item.name) // self.NAME_LENGTH) + 1 for item in self.items])
        return (row_count + 1) * self.ROW_HEIGHT + self.TITLE_HEIGHT


class MoneyDistributionFormHelper:

    def __init__(self, budget=None):
        self.budget = budget
        self.staff_salaries = budget.staffsalary_set.all()

    @property
    def sections(self):
        yield BudgetTable("Staff Salaries", self.staff_salary_items)
        yield BudgetTable("Communication", self.communication_items)
        yield BudgetTable("Travel", self.travel_items)
        yield BudgetTable("Administration", self.administration_items)
        yield BudgetTable("Medical", self.medical_items)
        yield BudgetTable("Miscellaneous", self.miscellaneous_items)
        yield BudgetTable("Shelter", self.shelter_items)
        yield BudgetTable("Food & Gas", self.food_gas_items)
        yield BudgetTable("Awareness", self.awareness_items)
        yield BudgetTable("Supplies", self.supplies_items)

    @property
    def total(self):
        return self.budget.station_total

    @property
    def date_entered(self):
        return self.budget.date_time_entered.date()

    @property
    def station_name(self):
        return self.budget.border_station.station_name

    @property
    def staff_salary_items(self):
        items = [BudgetLineItem(entry.staff_person.full_name, entry.salary) for entry in self.staff_salaries]
        return items + self.get_other_items(BorderStationBudgetCalculation.STAFF)

    @property
    def communication_items(self):
        items = []
        if self.budget.communication_chair:
            items.append(BudgetLineItem('Chair', self.budget.communication_chair_amount))
        if self.budget.communication_manager:
            items.append(BudgetLineItem('Manager', self.budget.communication_manager_amount))
        if self.budget.communication_number_of_staff_with_walkie_talkies > 0:
            title = 'Staff with Walkie Talkies (' + str(self.budget.communication_number_of_staff_with_walkie_talkies_multiplier) + ' each)'
            value = self.budget.communication_number_of_staff_with_walkie_talkies  * self.budget.communication_number_of_staff_with_walkie_talkies_multiplier
            items.append(BudgetLineItem(title, value))
        if self.budget.communication_each_staff > 0:
            title = 'Staff (' + str(self.budget.communication_each_staff_multiplier) + ' each)'
            value = self.budget.communication_each_staff * self.budget.communication_each_staff_multiplier
            items.append(BudgetLineItem(title, value))
        return items + self.get_other_items(BorderStationBudgetCalculation.COMMUNICATION)

    @property
    def travel_items(self):
        items = []
        if self.budget.travel_chair_with_bike:
            items.append(BudgetLineItem('Chair', self.budget.travel_chair_with_bike_amount))
        if self.budget.travel_manager_with_bike:
            items.append(BudgetLineItem('Manager', self.budget.travel_manager_with_bike_amount))
        staff_bikes_total = self.budget.travel_staff_bikes_total()
        if staff_bikes_total > 0:
            items.append(BudgetLineItem('Staff using bikes', staff_bikes_total))
        if self.budget.travel_last_months_expense_for_sending_girls_home > 0:
            items.append(BudgetLineItem('Sending girls home', self.budget.travel_last_months_expense_for_sending_girls_home))
        if self.budget.travel_motorbike:
            items.append(BudgetLineItem('Motorbike', self.budget.travel_motorbike_amount))
        if self.budget.travel_plus_other > 0:
            items.append(BudgetLineItem('Other', self.budget.travel_plus_other))
        return items + self.get_other_items(BorderStationBudgetCalculation.TRAVEL)

    @property
    def administration_items(self):
        items = []
        intercepts_total = self.budget.administration_intercepts_total()
        if intercepts_total > 0:
            items.append(BudgetLineItem('Intercepts', intercepts_total))
        meetings_total = self.budget.administration_meetings_total()
        if meetings_total > 0:
            items.append(BudgetLineItem('Meetings', meetings_total))
        if self.budget.administration_booth:
            items.append(BudgetLineItem('Booth', self.budget.administration_booth_amount))
        if self.budget.administration_registration:
            items.append(BudgetLineItem('Registration', self.budget.administration_registration_amount))
        return items + self.get_other_items(BorderStationBudgetCalculation.ADMINISTRATION)

    @property
    def medical_items(self):
        items = []
        if self.budget.medical_last_months_expense > 0:
            items.append(BudgetLineItem('Expense', self.budget.medical_last_months_expense))
        return items + self.get_other_items(BorderStationBudgetCalculation.MEDICAL)

    @property
    def miscellaneous_items(self):
        return self.get_other_items(BorderStationBudgetCalculation.MISCELLANEOUS)

    @property
    def shelter_items(self):
        items = []
        shelter_rent_and_utilities = self.budget.shelter_rent + self.budget.shelter_electricity + self.budget.shelter_water
        if shelter_rent_and_utilities > 0:
            items.append(BudgetLineItem('Rent (plus utilities)', shelter_rent_and_utilities))
        if self.budget.shelter_shelter_startup:
            items.append(BudgetLineItem('Shelter Startup', self.budget.shelter_shelter_startup_amount))
        if self.budget.shelter_shelter_two:
            items.append(BudgetLineItem('Shelter 2', self.budget.shelter_shelter_two_amount))
        return items + self.get_other_items(BorderStationBudgetCalculation.SHELTER)

    @property
    def food_gas_items(self):
        items = []
        intercepted_girls_total = self.budget.food_and_gas_intercepted_girls_total()
        limbo_girls_total = self.budget.food_and_gas_limbo_girls_total()
        if intercepted_girls_total > 0:
            items.append(BudgetLineItem('Intercepted Girls', intercepted_girls_total))
        if limbo_girls_total > 0:
            items.append(BudgetLineItem('Limbo Girls', limbo_girls_total))
        return items + self.get_other_items(BorderStationBudgetCalculation.FOOD_AND_GAS)

    @property
    def awareness_items(self):
        items = []
        if self.budget.awareness_contact_cards:
            items.append(BudgetLineItem('Contact Cards', self.budget.awareness_contact_cards_amount))
        if self.budget.awareness_awareness_party_boolean:
            items.append(BudgetLineItem('Awareness Party', self.budget.awareness_awareness_party))
        if self.budget.awareness_sign_boards_boolean:
            items.append(BudgetLineItem('Sign Boards', self.budget.awareness_sign_boards))
        return items + self.get_other_items(BorderStationBudgetCalculation.AWARENESS)

    @property
    def supplies_items(self):
        items = []
        if self.budget.supplies_walkie_talkies_boolean:
            items.append(BudgetLineItem('Walkie Talkies', self.budget.supplies_walkie_talkies_amount))
        if self.budget.supplies_recorders_boolean:
            items.append(BudgetLineItem('Recorders', self.budget.supplies_recorders_amount))
        if self.budget.supplies_binoculars_boolean:
            items.append(BudgetLineItem('Binoculars', self.budget.supplies_binoculars_amount))
        if self.budget.supplies_flashlights_boolean:
            items.append(BudgetLineItem('Flashlights', self.budget.supplies_flashlights_amount))
        return items + self.get_other_items(BorderStationBudgetCalculation.SUPPLIES)
    
    @property
    def notes(self):
        return self.budget.notes

    def get_other_items(self, section):
        other_items = self.budget.otherbudgetitemcost_set.filter(form_section=section)
        return [BudgetLineItem(item.name, item.cost) for item in other_items]

    @property
    def report_month(self):
        return self.budget.month_year.strftime('%B %Y')