from .export_form import ExportToGoogleSheet
from dataentry.form_data import FormData

class IrfGoogleSheet(ExportToGoogleSheet):
    def __init__(self, export_form):
        super().__init__(export_form)
        self.rows = []
        self.export_form = export_form
        
        for ei_card in export_form.ei_cards:
            if 'VICTIM' in ei_card.prefix.upper():
                self.victim_card = ei_card
            elif 'TRAFFICKER' in ei_card.prefix.upper():
                self.trafficker_card = ei_card
                
        headers = export_form.main_form.format_headers()
        element = export_form.category_dict[self.trafficker_card.category]
        headers = headers + element.format_headers(prefix=self.trafficker_card.prefix, max_count=self.trafficker_card.max_instances)
        element = export_form.category_dict[self.victim_card.category]
        headers = headers + element.format_headers(prefix=self.victim_card.prefix, max_count=self.victim_card.max_instances)
        
        self.rows.append(headers)
            
    def process_object(self, obj):
        base_row = []
        form_data = FormData(obj, self.export_form.export_import.form)
        
        for question in self.export_form.main_form.questions:
            base_row = base_row + question.export_value(form_data, form_data)
        for ie_field in self.export_form.main_form.fields:
            base_row.append(ie_field.export_value(form_data.form_object, form_data))
        
        # Both victim and trafficker are in the same category/card type
        category = self.victim_card.category
        cards = form_data.card_dict[category.id]
        questions_fields = self.export_form.category_dict[category]
        
        trafficker_count = 0
        for trafficker in cards:
            if trafficker.form_object.kind.upper() != 'T':
                # victim card
                continue
            
            trafficker_count += 1
            if trafficker_count > self.trafficker_card.max_instances:
                break
            
            for question in questions_fields.questions:
                base_row = base_row + question.export_value(trafficker, form_data)
            for ie_field in questions_fields.fields:
                base_row.append(ie_field.export_value(trafficker.form_object, form_data))
        
        remaining = self.trafficker_card.max_instances - trafficker_count
        for idx in range(0,remaining):
            for question in questions_fields.questions:
                base_row = base_row + question.export_value(None, form_data)
            for ie_field in questions_fields.fields:
                base_row.append('')
        
        for victim in cards:
            if victim.form_object.kind.upper() != 'V':
                continue
            
            row = list(base_row)
            
            for question in questions_fields.questions:
                row = row + question.export_value(victim, form_data)
            for ie_field in questions_fields.fields:
                row.append(ie_field.export_value(victim.form_object, form_data))
        
            self.rows.append(row)
            
        return self.rows
