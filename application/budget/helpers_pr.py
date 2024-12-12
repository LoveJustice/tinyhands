from collections import namedtuple

from time import strftime
from django.db.models import Q

from budget.models import BorderStationBudgetCalculation, OtherBudgetItemCost, ProjectRequest, ProjectRequestComment
from dataentry.models import BorderStation
from budget.helpers_base import Footnote, BudgetTable, StaffValue, StaffEntry
import budget.mdf_constants as constants

BudgetLineItem = namedtuple('budgetItem', ['name', 'value', 'footnote'])

class StaffData:
    def __init__(self, budget, project, footnote):
        self.staff_list = []
        self.staff_totals = []
        self.headers = ['Gross Pay', 'Deductions','Net Pay']
        self.footnote = footnote
        
        trailing_headers = ['Total']
        exclude_headers = ['Travel']
        
        # map desired header name to exisint type name
        convert_headers = {
            'Gross Pay':'Salary'
            }
        
        inverted_headers = {value: key for key, value in convert_headers.items()}
        
        staff_data = {}
        staff_order = []
        foot_note_count = 0
        
        # get headers based on all staff items
        staff_items = budget.requests.filter(category=constants.STAFF_BENEFITS).order_by('staff__first_name', 'staff__last_name', 'benefit_type_name')
        for staff_item in staff_items:
            if staff_item.benefit_type_name in inverted_headers:
                header_name = inverted_headers[staff_item.benefit_type_name]
            else:
                header_name = staff_item.benefit_type_name
            if header_name not in self.headers and header_name not in trailing_headers and header_name not in exclude_headers:
                self.headers.append(header_name)
        
        # get staff items for this 
        staff_items = budget.requests.filter(category=constants.STAFF_BENEFITS, project=project).order_by('staff__first_name', 'staff__last_name', 'benefit_type_name')
        for staff_item in staff_items:
            if staff_item.status == 'Approved-Completed' and staff_item.completed_date_time < budget.month_year:
                continue
            if staff_item.benefit_type_name in inverted_headers:
                header_name = inverted_headers[staff_item.benefit_type_name]
            else:
                header_name = staff_item.benefit_type_name
            if header_name not in self.headers:
                continue
            
            if staff_item.staff not in staff_order:
                staff_order.append(staff_item.staff)
            
            if staff_item.staff not in staff_data:
                staff_data[staff_item.staff] = {}
            if staff_item.description is not None and staff_item.description != '':
                foot_note = self.footnote.add_footnote(staff_item.description)
            else:
                foot_note = '';
            
            if staff_item.benefit_type_name in staff_data[staff_item.staff]:
                existing = staff_data[staff_item.staff][staff_item.benefit_type_name]
                staff_data[staff_item.staff][staff_item.benefit_type_name] = StaffValue(staff_item.cost + existing.cost, existing.foot_note + ' ' + foot_note)
            else:
                staff_data[staff_item.staff][staff_item.benefit_type_name] = StaffValue(staff_item.cost, foot_note)
        
        for staff in staff_order:
            if staff.last_name.find('general_staff') >= 0:
                continue
            self.staff_list.append(StaffEntry(staff, staff_data, self.headers, convert_headers))
        
        for idx in range(0, len(self.headers) + 1):
            total = 0
            for person_idx in range(0, len(self.staff_list)):
                value = self.staff_list[person_idx].values[idx]
                if value is not None and value.cost != '' and value.cost is not None:
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
        total = 0
        for idx in range(2,len(self.headers)):
            total += self.staff_totals[idx]
        return total
    
    def has_data(self):
        return len(self.staff_list) > 0
    
class MoneyNotSpentData:
    def __init__(self, budget, project):
        self.budget = budget
        self.items = []
        self.totals = {
            'deduct': 0,
            'not_deduct': 0
            }
        
        not_spent = self.budget.mdfitem_set.filter(
                category=constants.MONEY_NOT_SPENT, work_project=project).order_by('id')
        
        for item in not_spent:
            self.items.append ({
                'description': item.description,
                'section': item.associated_section_name,
                'deduct': item.deduct,
                'cost': item.cost
                })
            if item.deduct == 'Yes':
                self.totals['deduct'] += item.cost
            else:
                self.totals['not_deduct'] += item.cost
    
    def has_data(self):
        return len(self.items) > 0

class PastMonthSentMoney:
    def __init__(self, budget, project):
        self.budget = budget
        self.items = []
        self.total = 0
            
        past_sent = self.budget.mdfitem_set.filter(
                category=constants.PAST_MONTH_SENT, work_project=project).order_by('id')
        for item in past_sent:
            self.items.append ({
                'description': item.description,
                'section': item.associated_section_name,
                'cost': item.cost
                })
            self.total += item.cost
            
    def has_data(self):
        return len(self.items) > 0

class MdfCommentType:
    def __init__(self, budget, project, type):
        self.budget = budget
        self.project = project
        self.type = type
        
        if budget.status == 'Approved':
            item_qs = ProjectRequestComment.objects.filter(
                    Q(type=self.type) &
                    Q(request__project=self.project) &
                    Q(request__in=self.budget.requests.all()) & 
                    Q(mdf=self.budget))
        else:
            # if MDF is not yet approved, pick up comments where MDF reference is null
            item_qs = ProjectRequestComment.objects.filter(
                    Q(type=self.type) &
                    Q(request__project=self.project) &
                    Q(request__in=self.budget.requests.all()) & 
                    (Q(mdf=self.budget) | Q(mdf__isnull=True)))
        self.items = []
        for item in item_qs:
            self.items.append(item)
    
    @property
    def has_data(self):
        return len(self.items) > 0
    
    @property
    def item_list(self):
        return self.items

class MdfComments:
    def __init__(self, budget, project):
        self.changed = MdfCommentType(budget, project, 'Change Amount')
        self.declined = MdfCommentType(budget, project, 'Declined')
        self.completed = MdfCommentType(budget, project, 'Completed')
        self.pending = MdfPending(budget, project)
    
    @property
    def has_data(self):
        return self.changed.has_data or self.declined.has_data or self.completed.has_data or self.pending.has_data
        

class MdfPending:
    def __init__(self, budget, project):
        self.budget = budget
        self.project = project
    
    @property
    def has_data(self):
        return len(self.items) > 0
    
    @property
    def items(self):
        item_list = ProjectRequest.objects.filter(
                    status='Submitted', 
                    project=self.project,
                    override_mdf_project = self.budget.border_station,
                    date_time_entered__lt=self.budget.date_time_entered).order_by('category', 'staff__first_name', 'staff__last_name', 'benefit_type_name', 'description')
        return item_list
        

class MoneyDistributionFormProjectRequestHelper:

    def __init__(self, budget, project, first_page_footnote, second_page_footnote):
        self.budget = budget
        self.project = project
        self.staff_salaries = budget.requests.filter(category=constants.STAFF_BENEFITS)
        self.staff_data = StaffData(budget, project, first_page_footnote)
        self.money_not_spent_data = MoneyNotSpentData(budget, project)
        self.past_sent = PastMonthSentMoney(budget, project)
        self.second_footnote = second_page_footnote
        self.format = "{:,.2f}"
        self.comments = MdfComments(budget, project)
    
    @property
    def staff(self):
        return self.staff_data

    @property
    def sections(self):
        if self.budget.border_station == self.project:
            yield BudgetTable("Staff Salaries & Benefits", self.salary_and_benefit_items)
            yield BudgetTable("Rent & Utilities", self.rent_and_utilities_items)
            yield BudgetTable("Administration", self.administration_items)
            yield BudgetTable("Supplies & Awareness", self.supplies_and_awareness_items)
            yield BudgetTable("Staff Travel", self.staff_travel_items)
            yield BudgetTable("Potential Victim Care", self.potential_victim_care_items)
        else:
            yield BudgetTable("Staff Salaries & Benefits", self.salary_and_benefit_items)
            yield BudgetTable("Operational Expenses", self.operational_expense_items)
            
    
    
    @property
    def total_height(self):
        return 5 * BudgetTable.ROW_HEIGHT 
    
    @property
    def project_total(self):
        return self.budget.station_total(self.project)
    
    def project_total_formula(self):
        formula = '('
        sep = ''
        for section in self.sections:
            formula += sep + self.format.format(section.total) + ' (' + section.title + ')'
            sep = ' + '
                
        formula += ' = ' + self.format.format(self.project_total) + ')'
        return formula
    
    @property
    def distribution_total(self):
        return self.budget.station_total(self.project) - self.money_not_spent_total
    
    @property
    def distribution_total_formula(self):
        formula = '(' + self.format.format(self.project_total) + ' (Project Total) - '
        formula += self.format.format(self.money_not_spent_total) + ' (Money Not Spent) = '    
        formula += self.format.format(self.distribution_total) + ')'
        return formula
    
    @property
    def full_total(self):
        return self.distribution_total + self.budget.staff_salary_and_benefits_deductions(self.project) + self.past_money_sent_total
    
    @property
    def full_total_formula(self):
        formula = '(' + self.format.format(self.distribution_total) + ' (Monthly Distribution Subtotal) + '
        formula += self.format.format(self.budget.staff_salary_and_benefits_deductions(self.project)) + ' (Salary Deductions) + '
        formula += self.format.format(self.past_money_sent_total) + ' (Past Month Sent Money Subtotal) = '   
        formula += self.format.format(self.full_total) + ')'
        return formula

    @property
    def date_entered(self):
        return self.budget.date_time_entered.date()

    @property
    def station_name(self):
        return self.budget.border_station.station_name

    @property
    def salary_and_benefit_items(self):
        items = [BudgetLineItem('Salaries & benefits (breakdown on page 1)', self.staff_data.salaries_and_benefits_total,'')]
        return items
    
    @property
    def operational_expense_items(self):
        items = self.get_request_items(BorderStationBudgetCalculation.IMPACT_MULTIPLYING, self.project)
        return items

    @property
    def rent_and_utilities_items(self):
        items = []
        return items + self.get_request_items(BorderStationBudgetCalculation.RENT_UTILITIES, self.project)
        
    
    @property
    def administration_items(self):
        items = []
        return items + self.get_request_items(BorderStationBudgetCalculation.ADMINISTRATION, self.project)

    @property
    def staff_travel_items(self):
        items = []
        items += self.get_request_items(BorderStationBudgetCalculation.TRAVEL, self.project)
        return items

    @property
    def potential_victim_care_items(self):
        items = []
        return items + self.get_request_items(constants.POTENTIAL_VICTIM_CARE, self.project)
    
    @property
    def limbo_footnote(self):
        footnote = ''
        if self.budget.other_items_total(constants.LIMBO) > 0:
            for limbo in self.get_other_items(constants.LIMBO):
                if len(footnote) > 0:
                    footnote += ','
                footnote += limbo.name + '(' + str(self.budget.limbo_girls_multiplier * limbo.cost) + ')'
            footnote = '*1:' + footnote

        return footnote

    @property
    def supplies_and_awareness_items(self):
        items = []
        
        return items + self.get_request_items(constants.AWARENESS, self.project)
    
    @property
    def money_not_spent_total(self):
        total = 0
        not_spent_items = self.budget.mdfitem_set.filter(
                category=constants.MONEY_NOT_SPENT, work_project=self.project, deduct='Yes')
        for not_spent in not_spent_items:
            total += not_spent.cost
        return total
    
    @property
    def money_not_spent_items(self):
        items = [BudgetLineItem('Money Not Spent(to deduct) (breakdown on page 1)', self.money_not_spent_total,'')]
        return items
    
    @property
    def notes(self):
        return self.budget.notes
    
    def get_request_items(self, section, project):
        line_items = []
        request_items = self.budget.requests.filter(category=section, project=project, status__startswith='Approved')
        for item in request_items:
            if item.status == 'Approved-Completed' and item.completed_date_time < self.budget.month_year:
                continue
            if section == constants.POTENTIAL_VICTIM_CARE or section == constants.AWARENESS:
                line_items.append(BudgetLineItem(item.benefit_type_name + ':' + item.description, item.cost,'') )
            else:
                line_items.append(BudgetLineItem(item.description, item.cost,'') )
        return line_items

    def get_other_items(self, section, project):
        other_items = self.budget.mdfitem_set.filter(category=section, work_project=project)
        return [BudgetLineItem(item.name, item.cost,'') for item in other_items]
    
    def get_staff_items(self, benefit_type_name, project):
        staff_items = self.budget.staffbudgetitem_set.filter(benefit_type_name=benefit_type_name, work_project=project)
        items = []
        for item in staff_items:
            if item.cost is None:
                continue
            if item.description is not None and item.description != '':
                footnote = self.second_footnote.add_footnote(item.description)
            else:
                footnote = ''
            items.append(BudgetLineItem(item.staff.first_name + ' ' + item.staff.last_name, item.cost, footnote))
        return items
                

    @property
    def report_month(self):
        return self.budget.month_year.strftime('%B %Y')
    
    @property
    def past_month_sent_money(self):
        items = [BudgetLineItem('Past Month Sent Money (breakdown on page 1)', self.money_not_spent_total,'')]
        return items
    
    @property
    def past_money_sent_total(self):
        total = 0
        past_sent_items = self.budget.mdfitem_set.filter(
                category=constants.PAST_MONTH_SENT, work_project=self.project)
        for past_sent in past_sent_items:
            total += past_sent.cost
        return total
    
    @property
    def height_required(self):
        # for helping calculate the height required to render the project title
        # and the first budget tble for thep rojecct
        height = BudgetTable.TITLE_HEIGHT
        for section in self.sections:
            height += section.height_required
            break
        
        return height
    