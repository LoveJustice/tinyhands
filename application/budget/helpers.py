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

class StaffValue:
    def __init__(self, cost, foot_note):
        self.cost = cost
        self.foot_note = foot_note

class StaffEntry:
    def __init__(self, staff_person, staff_data, headers):
        self.name = staff_person.first_name + ' ' + staff_person.last_name
        self.values = []
        self.sub_total = 0
        
        total = 0
        for header in headers:
            if header in staff_data[staff_person]:
                value = staff_data[staff_person][header]
                if value is not None and value.cost is not None:
                    self.values.append(value)
                    total += value.cost
                else:
                     self.values.append(StaffValue('',''))
            else:
                self.values.append(StaffValue('',''))
        
        # sub total of salary and benefits        
        self.values.append(StaffValue(total,''))
        
        value = StaffValue('','')
        if 'Communication' in staff_data[staff_person]:
            value = staff_data[staff_person]['Communication']
            if value is not None and value.cost is not None:
                total += value.cost
            else:
                value = StaffValue('','')
        self.values.append(value)
        
        value = StaffValue('','')
        if 'Travel' in staff_data[staff_person]:
            value = staff_data[staff_person]['Travel']
            if value is not None and value.cost is not None:
                total += value.cost
            else:
                value = StaffValue('','')
        self.values.append(value)
        
        self.values.append(StaffValue(total,''))
        

class StaffData:
    def __init__(self, budget):
        self.staff_list = []
        self.staff_totals = []
        self.headers = ['Salary']
        self.foot_notes = []
        
        trailing_headers = ['Sub-Total', 'Communication', 'Travel', 'Total']
        
        staff_data = {}
        staff_order = []
        foot_note_count = 0
        staff_items = budget.staffbudgetitem_set.all().order_by('staff_person__first_name', 'staff_person__last_name', 'type_name')
        for staff_item in staff_items:
            if staff_item.type_name not in self.headers and staff_item.type_name not in trailing_headers:
                self.headers.append(staff_item.type_name)\
            
            if staff_item.staff_person not in staff_order:
                staff_order.append(staff_item.staff_person)
            
            if staff_item.staff_person not in staff_data:
                staff_data[staff_item.staff_person] = {}
            if staff_item.description is not None and staff_item.description != '':
                foot_note_count += 1
                foot_note = '*' + str(foot_note_count)
                self.foot_notes.append(foot_note + ":" + staff_item.description)
            else:
                foot_note = '';
            staff_data[staff_item.staff_person][staff_item.type_name] = StaffValue(staff_item.cost, foot_note)
        
        for staff_person in staff_order:
            if staff_person.last_name.find('general_staff') >= 0:
                continue
            self.staff_list.append(StaffEntry(staff_person, staff_data, self.headers))
        
        for idx in range(0, len(self.headers) + 4):
            total = 0
            for person_idx in range(0, len(self.staff_list)):
                value = self.staff_list[person_idx].values[idx]
                if value is not None and value.cost != '':
                    total += value.cost
            
            self.staff_totals.append(total)
    
    @property
    def added_headers(self):
        return self.headers
    
    @property
    def column_format(self):
        column_format = '20%'
        for idx in range(0, len(self.headers)+4):
            column_format += ' 8%'
    
        return column_format
    
    @property
    def salaries_and_benefits_total(self):
        return self.staff_totals[len(self.headers)]
    
    @property
    def communication_total(self):
        return self.staff_totals[len(self.headers)+1]
    
    @property
    def travel_total(self):
        return self.staff_totals[len(self.headers)+2]


class MoneyDistributionFormHelper:

    def __init__(self, budget=None):
        self.budget = budget
        self.staff_salaries = budget.staffbudgetitem_set.all()
        self.staff_data = StaffData(budget)
    
    @property
    def staff(self):
        return self.staff_data

    @property
    def sections(self):
        yield BudgetTable("Salaries & Benefits", self.salary_and_benefit_items)
        yield BudgetTable("Communication", self.communication_items)
        yield BudgetTable("Travel", self.travel_items)
        yield BudgetTable("Administration", self.administration_items)
        yield BudgetTable("Potential Victim Care", self.potential_victim_care_items)
        yield BudgetTable("Awareness", self.awareness_items)
        yield BudgetTable("Miscellaneous", self.miscellaneous_items)

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
    def salary_and_benefit_items(self):
        items = [BudgetLineItem('Salaries & benefits (breakdown on page 1)', self.staff_data.salaries_and_benefits_total)]
        return items + self.get_other_items(BorderStationBudgetCalculation.STAFF_BENEFITS)

    @property
    def communication_items(self):
        items = []
        if self.budget.communication_chair:
            items.append(BudgetLineItem('SC Chair', self.budget.communication_chair_amount))
        items.append(BudgetLineItem('Staff Communication', self.staff_data.communication_total))
        return items + self.get_other_items(BorderStationBudgetCalculation.COMMUNICATION)

    @property
    def travel_items(self):
        items = []
        if self.budget.travel_chair_with_bike:
            items.append(BudgetLineItem('SC Chair', self.budget.travel_chair_with_bike_amount))
        items.append(BudgetLineItem('Staff Travel', self.staff_data.travel_total))
        return items + self.get_other_items(BorderStationBudgetCalculation.TRAVEL)

    @property
    def administration_items(self):
        items = []
        intercepts_total = self.budget.administration_intercepts_total()
        if intercepts_total > 0:
            items.append(BudgetLineItem('Stationary', intercepts_total))
        meetings_total = self.budget.administration_meetings_total()
        if meetings_total > 0:
            items.append(BudgetLineItem('Meetings', meetings_total))
        if self.budget.administration_booth:
            items.append(BudgetLineItem('Booth', self.budget.administration_booth_amount))
        if self.budget.administration_office:
            items.append(BudgetLineItem('Office', self.budget.administration_office_amount))
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
    def potential_victim_care_items(self):
        items = []
        shelter_rent_and_utilities = 0
        if self.budget.shelter_rent:
            shelter_rent_and_utilities += self.budget.shelter_rent_amount
        if self.budget.shelter_electricity:
            shelter_rent_and_utilities += self.budget.shelter_electricity_amount
        if self.budget.shelter_water:
            shelter_rent_and_utilities += self.budget.shelter_water_amount
        if shelter_rent_and_utilities > 0:
            items.append(BudgetLineItem('Rent (plus utilities)', shelter_rent_and_utilities))
            
        intercepted_girls_total = self.budget.food_and_gas_intercepted_girls_total()
        limbo_girls_total = self.budget.food_and_gas_limbo_girls_total()
        if intercepted_girls_total > 0:
            items.append(BudgetLineItem('Intercepted Girls', intercepted_girls_total))
        if limbo_girls_total > 0:
            items.append(BudgetLineItem('Limbo Girls', limbo_girls_total))
        return items + self.get_other_items(BorderStationBudgetCalculation.POTENTIAL_VICTIM_CARE)

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
    def notes(self):
        return self.budget.notes

    def get_other_items(self, section):
        other_items = self.budget.otherbudgetitemcost_set.filter(form_section=section)
        return [BudgetLineItem(item.name, item.cost) for item in other_items]

    @property
    def report_month(self):
        return self.budget.month_year.strftime('%B %Y')