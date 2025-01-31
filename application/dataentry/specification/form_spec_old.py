from typing import List, Self
from dataentry.models import Storage


class StorageSpec:
    def __init__(self, tag: str, module_name: str, model_name: str, parent_storage: Self = None,
                 parent_field: str = None):
        self.tag = tag
        self.module_name = module_name
        self.model_name = model_name
        self.parent_storage = parent_storage
        self.parent_field = parent_field

    def remove_form_data(self):
        try:
            Storage.objects.get(form_tag=self.tag).delete()
        except:
            pass

    def find_form_data(self):
        result = {
            'db_obj': None,
            'errors': []
        }

        entries = Storage.objects.filter(form_tag=self.tag)
        if len(entries) > 0:
            result['db_obj'] = entries[0]
        else:
            storage = Storage()
            storage.form_tag = self.tag
            storage.module_name = self.module_name
            storage.model_name = self.model_name
            if self.parent_storage is not None:
                parent_result = self.parent_storage.find()
                if len(parent_result.errors) > 0:
                    result['errors'] = parent_result.errors
                else:
                    storage.parent_storage = parent_result['db_obj']
                    storage.parent_field = self.parent_field
                    storage.save()
                    result['db_obj'] = storage
            else:
                storage.save()
                result['db_obj'] = storage

        return result


class BaseQuestionSpec:
    def __init__(self, tag: str, answer_type: str, field_name: str, export_name, params: str = None,
                 export_params: str = None):
        self.tag = tag
        self.answer_type = answer_type
        self.field_name = field_name
        self.params = params
        self.export_name = export_name
        self.export_params = export_params


class CategorySpec:
    def __init__(self, tag: str, category_type: str, description: str, storage: StorageSpec = None):
        self.tag = tag
        self.category_type = category_type
        self.description = description
        self.storage = storage


class OptionsAndPointsSpec:
    def __init__(self, value: str, points: int):
        self.value = value
        self.points = points


class QuestionSpec:
    def __init__(self, base_question: BaseQuestionSpec, label: str, entry_type: str,
                 span: int = None, total: BaseQuestionSpec = None, points: int = None,
                 options: List[OptionsAndPointsSpec] = None,
                 other_option: OptionsAndPointsSpec = None):
        self.base_question = base_question
        self.label = label
        self.entry_type = entry_type
        self.span = span
        self.total = total
        self.points = points
        self.options = options
        self.other_option = other_option


class SubSectionSpec:
    def __init__(self, title: str, key: str, side: str, questions: List[QuestionSpec]):
        self.title = title
        self.key = key
        self.side = side
        self.questions = questions


class SectionSpec:
    def __init__(self, name: str, section_type: str, category: CategorySpec, subsections: List[SubSectionSpec]):
        self.name = name
        self.section_type = section_type
        self.category = category
        self.subsections = subsections


class ValidationSpec:
    def __init__(self, tag: str, level: str, validation_type: str, message: str, questions: List[BaseQuestionSpec],
                 trigger: BaseQuestionSpec = None, trigger_value: str = None, params: str = None,
                 on_retrieve: bool = False, on_update: bool = True):
        self.tag = tag
        self.level = level
        self.validation_type = validation_type
        self.message = message
        self.questions = questions
        self.trigger = trigger
        self.trigger_value = trigger_value
        self.params = params
        self.on_retrieve = on_retrieve
        self.on_update = on_update


class GoogleExportCardSpec:
    def __init__(self, category: CategorySpec, prefix: str, max_instances: int, index_field_name: str):
        self.category = category
        self.prefix = prefix
        self.max_instances = max_instances
        self.index_field_name = index_field_name


class GoogleExportFieldSpec:
    def __init__(self, field_name: str, answer_type: str, export_name: str, card: GoogleExportCardSpec = None,
                 arguments_json: str = None):
        self.field_name = field_name
        self.answer_type = answer_type
        self.export_name = export_name
        self.card = card
        self.arguments_json = arguments_json


class GoogleExportSpec:
    def __init__(self, tag: str, module_name: str, class_name: str, spreadsheet_name: str, sheet_name: str,
                 key_field_name: str, cards: List[GoogleExportCardSpec], fields: List[GoogleExportFieldSpec],
                 supress_warnings: bool = True):
        self.tag = tag
        self.module_name = module_name
        self.class_name = class_name
        self.spreadsheet_name = spreadsheet_name
        self.sheet_name = sheet_name
        self.key_field_name = key_field_name
        self.cards = cards
        self.fields = fields
        self.supress_warnings = supress_warnings


class FormSpec:
    def __init__(self, name: str, storage: StorageSpec, version: str, sections: List[SectionSpec],
                 validations: List[ValidationSpec] = None, export: GoogleExportFieldSpec = None):
        self.name = name
        self.storage = storage
        self.version = version
        self.sections = sections
        self.validations = validations
        self.export = export

    def generate_client_json(self):
        return ''

    def generate_form_data(self, client_json: str, form_type: str):
        pass
    def generate_form(self, form_type: str):
        client_json = self.generate_client_json()
        self.generate_form_data(client_json, form_type)

class FormsOfTypeSpec:
    def __init__(self, form_type: str, form_specs: List[FormSpec]):
        self.form_type = form_type
        self.form_specs = form_specs

    def generate_forms(self):
        for form in self.form_specs:
            form.generate_form(self.form_type)

