import logging
from django.core.exceptions import ObjectDoesNotExist

from dataentry.models import ExportImportCard, ExportImportField, Form, FormCategory, FormType, GoogleSheetConfig, QuestionLayout
from dataentry.form_data import FormData

logger = logging.getLogger(__name__);

class ExportElement:
    def __init__(self):
        self.questions = []
        self.fields = []
        
    def format_headers(self, prefix = '', max_count=1):
        headers = []
        for cnt in range(1,max_count+1):
            if '%d' in prefix:
                iter_prefix = prefix % cnt
            else:
                iter_prefix = prefix    
            for question in self.questions:
                headers = headers + question.export_headers(iter_prefix)
            for field in self.fields:
                headers.append(iter_prefix + field.export_name)
        
        return headers
    
class ExportForm:
    def __init__(self, google_sheet_config):
        self.google_sheet_config = google_sheet_config
        self.export_import = google_sheet_config.export_import
        self.main_form = ExportElement()
        self.category_dict = {}
        
        self.ei_cards = ExportImportCard.objects.filter(export_import = self.export_import)
        for ei_card in self.ei_cards:
            self.category_dict[ei_card.category] = ExportElement()
        
        form_categories = FormCategory.objects.filter(form=self.export_import.form)
        category_list = []
        for form_category in form_categories:
            category_list.append(form_category.category)
            
        question_layouts = QuestionLayout.objects.filter(category__in = category_list).order_by('category__id', 'question__id')
        for question_layout in question_layouts:
            category = question_layout.category
            if category.category_type.name == 'card':
                if category in self.category_dict:
                    self.category_dict[category].questions.append(question_layout.question)
            else:
                self.main_form.questions.append(question_layout.question)
        
        ei_fields = ExportImportField.objects.filter(export_import = self.export_import)
        for ei_field in ei_fields:
            if ei_field.card is None:
                self.main_form.fields.append(ei_field)
            else:
                category = ei_field.card.category
                if category in self.category_dict:
                    self.category_dict[category].fields.append(ei_field)
        
        self.headers = self.main_form.format_headers()
        for ei_card in self.ei_cards:
            element = self.category_dict[ei_card.category]
            self.headers = self.headers + element.format_headers(prefix=ei_card.prefix, max_count=ei_card.max_instances)
    
    def get_category(self, category_id):
        for category in self.category_dict.keys():
            if category_id == category.id:
                return category
        
        return None

class ExportFormFactory:
    form_type_dict = {}
    form_dict = {}
    
    @staticmethod
    def find(border_station, form_type):
        if form_type not in ExportFormFactory.form_type_dict:
            ExportFormFactory.form_type_dict[form_type] = {}
        
        if border_station in ExportFormFactory.form_type_dict[form_type]:
            export_forms = ExportFormFactory.form_type_dict[form_type][border_station]
        else:
            try:
                form = Form.objects.get(form_type=form_type, stations=border_station)
                if form in ExportFormFactory.form_dict:
                    export_forms = ExportFormFactory.form_dict[form]
                    ExportFormFactory.form_type_dict[form_type][border_station] = export_forms
                else:
                    export_forms = []
                    google_sheet_list = GoogleSheetConfig.objects.filter(export_import__form = form, export_or_import='export')
                    for google_sheet in google_sheet_list:
                        export_form = ExportForm(google_sheet)
                        export_forms.append(export_form)
                    ExportFormFactory.form_dict[form] = export_forms
                    ExportFormFactory.form_type_dict[form_type][border_station] = export_forms
            except ObjectDoesNotExist:
                export_forms = []
                ExportFormFactory.form_type_dict[form_type][border_station] = export_forms
        
        return export_forms
    
    @staticmethod
    def find_by_instance(form_instance):
        station = form_instance.station
        form_type = FormType.objects.get(name=form_instance.get_form_type_name())
        return ExportFormFactory.find(station, form_type)
    
class ExportToGoogleSheet:
    def __init__(self, export_form):
        self.export_form = export_form
        self.google_sheet_config = export_form.google_sheet_config
        self.rows = []
        self.rows.append(export_form.headers)
    
    def process_object_list(self, obj_list):
        for obj in obj_list:
            process_object(obj)
    
    def export_card_data(self, card_data, form_data, questions_fields):
        row = []
        for question in questions_fields.questions:
            row = row + question.export_value(card_data, form_data)
        for ie_field in questions_fields.fields:
            row.append(ie_field.export_value(card_data.form_object, form_data))
        return row
    
    def export_blank_card(self, form_data, questions_fields):
        row = []
        for question in questions_fields.questions:
            row = row + question.export_value(None, form_data)
        for _ in questions_fields.fields:
            row.append('')
        return row
    
    def process_unindexed_card(self, cards, ei_card, form_data, questions_fields):
        row = []
        limit = min(len(cards), ei_card.max_instances)
        for idx in range(0,limit):
            row = row + self.export_card_data(cards[idx], form_data, questions_fields)
        
        for idx in range(0, ei_card.max_instances - limit):
            row = row + self.export_blank_card(form_data, questions_fields)
        return row
    
    def process_indexed_card(self, cards, ei_card, form_data, questions_fields):
        row = []
        for idx in range(0, ei_card.max_instances):
            found = False
            for card_data in cards:
                if getattr(card_data.form_object, ei_card.index_field_name, None) == idx+1:
                    found = True
                    row = row + self.export_card_data(card_data, form_data, questions_fields)
                    break
                
            if not found:
                row = row + self.export_blank_card(form_data, questions_fields)
                  
        return row
    
    def process_object(self, obj):
        row = []
        form_data = FormData(obj, self.export_form.export_import.form)
        
        for question in self.export_form.main_form.questions:
            row = row + question.export_value(form_data, form_data)
        for ie_field in self.export_form.main_form.fields:
            row.append(ie_field.export_value(form_data.form_object, form_data))
 
        for ei_card in self.export_form.ei_cards:
            category_id = ei_card.category.id
            category = self.export_form.get_category(category_id)
            if category is None or category not in self.export_form.category_dict:
                continue
        
            cards = form_data.card_dict[category_id]
            if cards is None:
                cards = []
                
            questions_fields = self.export_form.category_dict[category]
            if ei_card.index_field_name is None:
                row = row + self.process_unindexed_card(cards, ei_card, form_data, questions_fields)
            else:
                row = row + self.process_indexed_card(cards, ei_card, form_data, questions_fields)

        self.rows.append(row)
        return row
    
    @staticmethod
    def audit_forms():
        logger.info("Begin audit_forms")
        audit_sheets = GoogleSheetConfig.objects.filter(export_or_import='export')
        for audit_sheet in audit_sheets:
            logger.info("Begin audit of form " + audit_sheet.export_import.form.form_name)
            stations = audit_sheet.export_import.form.stations.all()
            if len(stations) < 1:
                # no stations for the form, so we cannot audit
                continue
            
            storage = audit_sheet.export_import.form.storage
            mod = __import__(storage.module_name, fromlist=[storage.form_model_name])
            form_model = getattr(mod, storage.form_model_name, None)
            forms_to_audit = form_model.objects.filter(status='approved', station__in=stations)
            if len(forms_to_audit) < 1:
                # no forms to audit
                continue
            
            export_form = ExportFormFactory.find_by_instance(forms_to_audit[0])
            factory = ExportToGoogleSheetFactory()
            export_sheet = factory.find(export_form[0])
            mod = __import__('export_import.google_sheet', fromlist=['GoogleSheet'])
            google_sheet_class = getattr(mod, 'GoogleSheet', None)
            google_sheet = google_sheet_class.from_form_config(export_sheet.google_sheet_config)
            google_sheet.audit(forms_to_audit, forms_to_audit[0].key_field_name())
            logger.info("Complete audit of form " + audit_sheet.export_import.form.form_name)
        
        logger.info("Complete audit_forms")

class ExportToGoogleSheetFactory:
    def __init__(self):
        self.google_exports = {}
    
    def find(self, export_form):
        if export_form.google_sheet_config in self.google_exports:
            export_to_google_sheet =  self.google_exports[export_form.google_sheet_config]
        else:
            module = export_form.export_import.implement_module
            if module is None:
               export_to_google_sheet = None
            else:
                class_name = export_form.export_import.implement_class_name
                mod = __import__(module, fromlist=[class_name])
                export_class = getattr(mod, class_name)
                export_to_google_sheet = export_class(export_form)
            self.google_exports[export_form.google_sheet_config] = export_to_google_sheet

        return export_to_google_sheet
        
            
            
            
