from dataentry.models import GoogleSheet
from _bsddb import DB_FCNTL_LOCKING

class ExportMapElement:
    def __init__(self):
        self.questions = []
        self.fields = []
    
    def format_headers(self, prefix = '', max_count=1):
        headers = []
        for cnt in range(1..max_count+1):
            if '%d' in prefix:
                iter_prefix = prefix % cnt
            else:
                iter_prefix = prefix    
            for question in self.questions:
                headers.append(iter_prefix + question.export_header)
            for field in self.fields:
                headers.append(iter_prefix + field.export_header)
        
        return headers
            
        
class ExportMapping:
    def __init__(self, country):
        self.google_sheet = GoogleSheet.objects.get(export_import__form_country=country,
                                        export_import__form__form_type__name='IRF', export_or_import-'export')
        
        question_to_category = {}
        question_layouts = QuestionLayout.objects.filter(category__form = self.google_sheet.export_import.form)
        for question_layout in question_layouts:
            question_to_category[question] = question_layout.category
        
        self.main_form = ExportMapElement()
        self.category_dict = {}
        
        self.ei_cards = ExportImportCard.objects.filter(export_import = self.google_sheet.export_import)
        for ei_card in self.ei_cards:
            self.category_dict[ei_card.category] = ExportMapElement()
        
        ei_questions = ExportImportQuestion.filter(export_import = self.google_sheet.export_import)
        for ei_question in ei_questions:
            if ei_question.question in question_to_category:
                category = question_to_category[ei_question.question]
                if category.category_type.name == 'card':
                    if category in self.category_dict:
                        self.category_dict[category].questions.append(ei_question)
                    else:
                        pass    #error card question but no ExportImportCard
                else:
                    # not a card question - in main form
                    self.main_form.questions.append(ei_question)
            else:
                pass    #error question is not associated with the form to be exported
        
        ei_fields = ExportImportField.filter(export_import = self.google_sheet.export_import)
        for ei_field in ei_fields:
            if ei_field.card is None:
                self.main_form.fields.append(ei_field)
            else:
                category = ei_field.card.category
                if category in self.category_dict:
                    self.category_dict[category].fields.append(ei_field)
                else:
                    pass    # error
        
        self.headers = self.main_form.format_headers()
        for ei_card in self.ei_cards:
            element = self.category_dict[ei_card.category]
            self.headers = self.headers + element.format_headers(prefix=ei_card.prefix, max_count=ei_card.max_instances)

irf_export_cache = {}

def get_export_mapping(country):
    if country not in irf_export_cache:
        irf_export_cache[country] = ExportMapping(country)
        
    return irf_export_cache[country]

def get_irf_export_rows(irfs):
    if len(irfs) < 1:
        return []
    
    country = irfs[0].station.operating_country
    
    mapping = get_export_mapping(country)
    
    rows = []
    rows.append(mapping.headers)
    
    for ei_card in mapping.ei_cards:
        if 'VICTIM' in iecard.prefix.upper():
            victim_card = ei_card
        else:
            trafficker_card = ei_card
    
    for irf in irfs:
        main_form_row = []
        form_data = FormData(irf, mapping.google_sheet.export_import.form)
        
        for ie_question in mapping.main_form.questions:
            main_form_row.append(form_data.get_answer(ie_question.question))
        for ie_field in mapping.main_form.fields:
            main_form_row.append(form_data.get_field(ie_field.field_name))
        
        # Both victim and trafficker cards are the same category  
        cards = form_data.card_dict[victim_card.category.id]
        
        # Same traffickers repeated for each victim
        traf_cnt = 0
        traf_row = []
        for trafficker in cards:
            if trafficker.form_object.kind != 't':
                continue
            
            traf_cnt = traf_cnt + 1
            for ie_question in mapping.card_dict[trafficker_card.category].questions:
                 traf_row.append(trafficker.get_answer(ie_question.question))
            for ie_field in mapping.card_dict[trafficker_card.category].fields:
                 traf_row.append(trafficker.get_field(ie_field.field_name))
        
        remaining_cnt = trafficker_card.max_instances - traf_cnt
        for cnt in (0..remaining_cnt):
            for ie_question in mapping.card_dict[trafficker_card.category].questions:
                 traf_row.append('')
            for ie_field in mapping.card_dict[trafficker_card.category].fields:
                 traf_row.append('')
            
            
        for victim in cards:
            if victim.form_object.kind != 'v':
                # Not a victim
                continue
            
            row = list(main_form_row)
            for ie_question in mapping.card_dict[victim_card.category].questions:
                row.append(victim.get_answer(ie_question.question))
            for ie_field in mapping.card_dict[victim_card.category].fields:
                row.append(victim.get_field(ie_field.field_name))
            
            row = row + traf_row
                
            rows.appen(row)
        
    return rows
