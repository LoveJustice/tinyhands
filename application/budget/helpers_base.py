class Footnote:
    def __init__(self):
        self.footnotes = []
    
    def add_footnote(self, text):
        footnote = '*' + str(len(self.footnotes)+1)
        self.footnotes.append(footnote + ":" + text)
        return footnote
    
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
    def __init__(self, staff_person, staff_data, headers, convert_headers):
        self.name = staff_person.first_name + ' ' + staff_person.last_name
        self.values = []
        sub_total = 0
        
        total = 0
        for header in headers:
            if header in convert_headers:
                find_header = convert_headers[header]
            else:
                find_header = header
            
            if find_header in staff_data[staff_person]:
                value = staff_data[staff_person][find_header]
                if value is not None and value.cost is not None:
                    self.values.append(value)
                    if header == 'Deductions':
                        total -= value.cost
                        sub_total -= value.cost
                    else:
                        total += value.cost
                        if header == 'Gross Pay':
                            sub_total += value.cost
                else:
                     self.values.append(StaffValue('',''))
            else:
                if header == 'Net Pay':
                    self.values.append(StaffValue(sub_total, ''))
                else:
                    self.values.append(StaffValue('',''))
        
        self.values.append(StaffValue(total,''))