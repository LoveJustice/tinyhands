from __future__ import annotations  # Needed for recursive types
from typing import List, TypedDict
from django.db.models import Q
from django.db import transaction
from django.core.exceptions import FieldDoesNotExist

from dataentry.specification.form_spec import FormsOfTypeSpec, FormSpec, GoogleExportSpec, QuestionSpec, SectionSpec
from dataentry.specification.form_spec import StorageSpec, SubSectionSpec, ValidationSpec
from dataentry.models import AnswerType, Category, CategoryType, ExportImport, ExportImportCard, ExportImportField, Form
from dataentry.models import FormCategory, FormType, FormValidation, FormValidationLevel, FormValidationQuestion
from dataentry.models import FormValidationType, GoogleSheetConfig, Storage, Question, QuestionLayout, QuestionStorage

class FormSpecTracking(TypedDict):
    form_type: str
    version: str
    form: object
    main_storage: object | None
    card_name: str | None
    card_storage: object | None
    main_tags: List[str]
    card_tags: dict[str, List[str]]
    errors: List[str]


def version_tag(plain_tag: str, tracking: FormSpecTracking):
    return plain_tag + '.' + tracking['version']


def storage_model(storage: StorageSpec, tracking: FormSpecTracking):
    module_name = storage['module_name']
    form_model_name = storage['model_name']
    mod = __import__(module_name, fromlist=[form_model_name])
    form_class = getattr(mod, form_model_name, None)
    if form_class is None:
        tracking['errors'].append("Storage model not found for module '%s' model '%s'" % (module_name, form_model_name))
    return form_class


def generate_question_json(question: QuestionSpec):
    result = {
        "label": question["label"],
        "formField": question["base_question"]["tag"],
        "type": question["entry_type"],
    }
    if question["span"] is not None:
        result["span"] = question["span"]
    if question["total"] is not None:
        result["refFlagTotalField"] = question["total"]["tag"]
    if question["points"] is not None:
        result["refFlagPoints"] = question["points"]
    if question["options"] is not None:
        result["options"] = []
        for option in question["options"]:
            entry = {
                "value": option["value"],
                "redFlagPoints": option["points"],
            }
            result["options"].append(entry)
        if question["other_option"] is not None:
            result["otherOption"] = {
                "value": question["other_option"]["value"],
                "redFlagPoints": question["other_option"]["points"],
            }

    return result


def generate_subsection_json(sub: SubSectionSpec):
    result = {
        "subsectionKey": sub['key'],
        "sideOfPage": sub["side"],
    }
    if sub['title'] is not None:
        result['subsectionTitle'] = sub['title']
    result['questions'] = []
    for question in sub['questions']:
        result['questions'].append(generate_question_json(question))
    return result


def generate_form_json(spec: FormSpec):
    result = {"sections": []}
    for section in spec['sections']:
        sect = {
            "name": section['name'],
            "type": section['category']['category_type'],
            "subsections": []
        }
        for subsection in section['subsections']:
            sub = generate_subsection_json(subsection)
            sect['subsections'].append(sub)
        result["sections"].append(sect)

    return result


def upsert(model, keys, values):
    query = Q()
    for (field, value) in keys.items():
        query &= Q(**{field: value})
    matched = model.objects.filter(query)
    if len(matched) > 1:
        return  # error
    elif len(matched) == 1:
        entry = matched[0]
    else:
        entry = model()
        for (field, value) in keys.items():
            setattr(entry, field, value)
    for (field, value) in values.items():
        setattr(entry, field, value)

    entry.save()
    return entry


def update_google_export(google: GoogleExportSpec, tracking):
    export_import = upsert(ExportImport, {'form_tag': version_tag(google['tag'], tracking)}, {
        'description': 'export form ' + tracking['form'].form_name,
        'implement_module': google['module_name'],
        'implement_class_name': google['class_name'],
        'form_id': tracking['form'].id,
    })
    upsert(GoogleSheetConfig, {'export_import_id': export_import.id},{
        'export_or_import': 'export',
        'spreadsheet_name': google['spreadsheet_name'],
        'sheet_name': google['sheet_name'],
        'key_field_name': google['key_field_name'],
        'suppress_column_warnings': google['suppress_warnings'],
    })
    for card in google['cards']:
        category = Category.objects.get(form_tag=card['category']['tag'])
        upsert(ExportImportCard, {'export_import_id': export_import.id, 'category_id': category.id}, {
            'prefix': card['prefix'],
            'max_instances': card['max_instances'],
            'index_field_name': card['index_field_name'],
        })
    for field in google['fields']:
        if field['card'] is not None:
            category = Category.objects.get(form_tag=field['card']['tag'])
            field_card = ExportImportCard.objects.get(export_import=export_import, card_id=category.id)
        else:
            field_card = None
        upsert(ExportImportField, {
            'export_import_id': export_import.id,
            'card': field_card,
            'field_name': field['field_name']}, {
            'answer_type': field['answer_type'],
            'export_name': field['export_name'],
            'arguments_json': field['argument_json'],
        })


def update_validation(validation: ValidationSpec, tracking: FormSpecTracking):
    level = FormValidationLevel.objects.get(name=validation['level'])
    validation_type = FormValidationType.objects.get(name=validation['validation_type'])
    if validation['trigger'] is not None:
        trigger = Question.objects.get(form_tag=version_tag(validation['trigger']['tag'], tracking))
    else:
        trigger = None
    validation = upsert(FormValidation, {'form_tag': version_tag(validation['tag'], tracking),},{
        'level': level,
        'validation_type': validation_type,
        'trigger': trigger,
        'trigger_value': validation['trigger_value'],
        'params': validation['params'],
        'retrieve': validation['on_retrieve'],
        'update': validation['on_update'],
                            })
    for question_tag in validation['questions']:
        question = Question.objects.get(form_tag=version_tag(question_tag, tracking))
        upsert(FormValidationQuestion, {'formvalidation_id': validation.id, 'question_id': question.id}, {})
    validation.forms.add(tracking['form'])
    return validation


def update_category(section: SectionSpec, tracking: FormSpecTracking):
    category_tag = version_tag(section['category']['tag'], tracking)
    if section['category']['storage'] is not None:
        category_storage = storage_model(section['category']['storage'], tracking)
        check_model = category_storage
    else:
        category_storage = None
        check_model = tracking['main_storage']
    category_type = CategoryType.objects.get(name=section['category']['category_type'])
    category = upsert(Category, {'form_tag': category_tag}, {
        'category_type': category_type,
        'description': section['category']['description'],
        'storage': category_storage,
    })
    for subsection in section['subsections']:
        for question in subsection['questions']:
            try:
                check_model._meta.get_field(question['base_question']['field_name'])
            except FieldDoesNotExist:
                tracking['errors'].append('Question storage field ' + question['base_question']['field_name'] +
                                          ' is not found for question ' + question['base_question']['tag'])
                continue
            answer_type = AnswerType.objects.get(name=question['base_question']['answer_type'])
            question_obj = upsert(Question, {'form_tag': version_tag(question['base_question']['tag'], tracking)}, {
                "answer_type": answer_type,
                "params": question["base_question"]['params'],
                "export_name": question["base_question"]['export_params'],
                "export_params": question["base_question"]['export_params'],
            })
            if question['points'] is not None or question['options'] is not None or question['other_option'] is not None:
                flag_points = {
                    'points': question['points'],
                    'options': question['options'],
                    'other_option': question['other_option'],
                }
            else:
                flag_points = None
            upsert(QuestionStorage, {
                'question_id': question_obj.id,},
                   {'field_name': question['base_question']['field_name'],
            })
            upsert(QuestionLayout, {'category_id': category.id, 'question_id': question_obj.id}, {
                'flag_points': flag_points,
            })
            if category_storage is None:
                if question['base_question']['tag'] not in tracking['main_tags']:
                    tracking['main_tags'].append(question['base_question']['tag'])
                else:
                    if section['category']['tag'] not in tracking['card_tags']:
                        tracking['card_tags'][section['category']['tag']] = []
                    tracking['card_tags'][section['category']['tag']].append(question['base_question']['tag'])

    return category


def clean_model (model, version):
    end_match = '.' + version
    remove_qs = model.objects.filter(form_tag__endswith=end_match)
    for to_remove in remove_qs:
        to_remove.delete()


def clean_version (version: str):
    clean_model(FormValidation, version)
    clean_model(ExportImport, version)
    clean_model(Question, version)
    clean_model(Category, version)
    clean_model(Storage, version)


class GenerateErrors(Exception):
    def __init__(self, text):
        # Custom attributes
        self.text = text


def generate_form_spec(spec: FormsOfTypeSpec):
    tracking: FormSpecTracking = {
        'form_type': spec['form_type'],
        'version': spec['version'],
        'form': None,
        'main_storage': None,
        'card_name': None,
        'card_storage': None,
        'main_tags': [],
        'card_tags': {},
        'errors': [],
    }

    try:
        with transaction.atomic():
            clean_version(spec['version'])
            form_type = FormType.objects.get(name=tracking['form_type'])
            for form_spec in spec['form_specs']:
                client_json = generate_form_json(form_spec)
                storage = storage_model(form_spec['storage'], tracking)
                if storage is None:
                    continue
                else:
                    tracking['main_storage'] = storage
                storage_tag = version_tag(form_spec['storage']['tag'], tracking)
                storage_object = upsert(Storage, {'form_tag': storage_tag}, {
                    'module_name': form_spec['storage']['module_name'],
                    'form_model_name': form_spec['storage']['model_name'],
                })
                form = upsert(Form, {'form_name': form_spec['name']},
                              {'form_type': form_type,
                               'storage': storage_object,
                               'start_date': '',
                               'end_date': '2118-12-31',
                               'version': spec['version'],
                               'client_json': client_json,
                               'use_tag_suffix': True,
                               })
                tracking['form'] = form
                category_index = 1
                for section in form_spec['sections']:
                    category = update_category(section, tracking)
                    upsert(FormCategory, {
                        "form": form,
                        "category": category,
                        "order": category_index,
                    }, {"name": "tbd"})
                for validation in form_spec['validations']:
                    update_validation(validation, tracking)
                if form_spec['export'] is not None:
                    update_google_export(form_spec['export'], tracking)
            if len(tracking['errors']) > 0:
                raise GenerateErrors('Errors occurred')
    except GenerateErrors as e:
        print('errors occurred during generation')

    return tracking
