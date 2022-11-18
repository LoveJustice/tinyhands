from export_import import form_data_serializer
from dataentry.models.form import *

class Serializer(form_data_serializer.Serializer):
    def init_adjustments(self):
        self.adjustments[FormType] = {'dropId':False}
        self.adjustments[CategoryType] = {'dropId':False}
        self.adjustments[AnswerType] = {'dropId':False}
        self.adjustments[FormValidationLevel] = {'dropId':False}
        self.adjustments[FormValidationType] = {'dropId':False} 
            
        self.adjustments[Storage] = {'dropId':False}
        self.adjustments[Form] = {'dropId': False, 'clear-m2m': 'stations'}
        self.adjustments[Category] = {'dropId': False}
        self.adjustments[FormCategory] = {'dropId': True}
        self.adjustments[Question] = {'dropId': False}
        self.adjustments[QuestionLayout] = {'dropId': True}
        self.adjustments[QuestionStorage] = {'dropId': True}
        self.adjustments[Answer] = {'dropId': True}
        self.adjustments[FormValidation] = {'dropId': False}
        self.adjustments[FormValidationQuestion] = {'dropId': True}
        self.adjustments[ExportImport] = {'dropId': False}
        self.adjustments[ExportImportCard] = {'dropId': True}
        self.adjustments[ExportImportField] = {'dropId': True}
        self.adjustments[GoogleSheetConfig] = {'dropId': True}
    
    def start_serialization(self):
        self.init_adjustments()
        return super(Serializer, self).start_serialization()