from __future__ import annotations  # Needed for recursive types
import json
import datetime
from typing import List, TypedDict
from django.db.models import Q
from django.db import transaction
from django.core.exceptions import FieldDoesNotExist

from specification.form_spec import BaseQuestionSpec, FormsOfTypeSpec, FormSpec, GoogleExportSpec, QuestionSpec
from specification.form_spec import SectionSpec, StorageSpec, SubSectionSpec, ValidationSpec
from dataentry.models import AnswerType, Category, CategoryType, ExportImport, ExportImportCard, ExportImportField, Form
from dataentry.models import FormCategory, FormType, FormValidation, FormValidationLevel, FormValidationQuestion
from dataentry.models import FormValidationType, GoogleSheetConfig, Storage, Question, QuestionLayout, QuestionStorage


class FormSpecTracking(TypedDict):
    form_type: str
    version: str
    form: object
    main_storage_model: object | None
    main_storage_object: object
    main_tags: List[str]
    card_tags: dict[str, List[str]]
    client_json: dict[str, str]
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
    if question["total_question"] is not None:
        result["flagTotalQuestions"] = []
        for total_question in question["total_question"]:
            result["flagTotalQuestions"].append(total_question['tag'])

    if question["points"] is not None:
        result["flagPoints"] = question["points"]
    if question["options"] is not None:
        result["options"] = []
        for option in question["options"]:
            entry = {
                "value": option["value"],
                "flagPoints": option["points"],
            }
            result["options"].append(entry)
        if question["other_option"] is not None:
            result["otherOption"] = {
                "value": question["other_option"]["value"],
                "flagPoints": question["other_option"]["points"],
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
    result = {
        "name": spec['name'],
        "sections": []
    }
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
        raise GenerateErrors('More than one row for model ' + str(model) + ' key ' + str(keys))
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
    upsert(GoogleSheetConfig, {'export_import_id': export_import.id}, {
        'export_or_import': 'export',
        'spreadsheet_name': google['spreadsheet_name'],
        'sheet_name': google['sheet_name'],
        'key_field_name': google['key_field_name'],
        'suppress_column_warnings': google['suppress_warnings'],
    })
    for card in google['cards']:
        try:
            category = Category.objects.get(form_tag=version_tag(card['category']['tag'], tracking))
        except Category.DoesNotExist:
            raise GenerateErrors('Category for export not found for category tag ' + card['category']['tag'])
        upsert(ExportImportCard,
               {'export_import_id': export_import.id, 'category_id': category.id, 'prefix': card['prefix']}, {
                   'max_instances': card['max_instances'],
                   'index_field_name': card['index_field_name'],
               })
    for field in google['fields']:
        if field['card'] is not None:
            try:
                category = Category.objects.get(form_tag=field['card']['tag'])
            except Category.DoesNotExist:
                raise GenerateErrors('Category not found for card ' + field['card']['tag'])
            field_card = ExportImportCard.objects.get(export_import=export_import, card_id=category.id)
        else:
            field_card = None
        try:
            answer_type = AnswerType.objects.get(name=field['answer_type'])
        except AnswerType.DoesNotExist:
            raise GenerateErrors('Answer type ' + field['answer_type'] + ' not found for field ' + field['card']['tag'])
        upsert(ExportImportField, {
            'export_import_id': export_import.id,
            'card': field_card,
            'field_name': field['field_name']}, {
                   'answer_type': answer_type,
                   'export_name': field['export_name'],
                   'arguments_json': field['argument_json'],
               })


def param_version_traverse(nested_list, tracking: FormSpecTracking):
    for key, value in nested_list.items():
        if isinstance(value, dict):
            param_version_traverse(value, tracking)
        else:
            if key == 'question_tag' or key == 'count_question_tag':
                nested_list[key] = version_tag(value, tracking)
    return nested_list


def update_validation(validation: ValidationSpec, tracking: FormSpecTracking):
    try:
        level = FormValidationLevel.objects.get(name=validation['level'])
    except FormValidationLevel.DoesNotExist:
        raise GenerateErrors('Level ' + validation['level'] + ' not found for validation ' + validation['tag'])
    try:
        validation_type = FormValidationType.objects.get(name=validation['validation_type'])
    except FormValidationType.DoesNotExist:
        raise GenerateErrors(
            'Validation type ' + validation['validation_type'] + ' not found for validation ' + validation['tag'])
    if validation['trigger'] is not None:
        question: BaseQuestionSpec = validation['trigger']
        try:
            trigger = Question.objects.get(form_tag=version_tag(question['tag'], tracking))
        except Question.DoesNotExist:
            raise GenerateErrors(
                'Trigger question ' + question['tag'] + ' not found for validation ' + validation['tag'])
    else:
        trigger = None
    if validation['params'] is not None:
        # find question tags and make them version tags
        params = param_version_traverse(validation['params'], tracking)
    else:
        params = None
    validation_object = upsert(FormValidation, {'form_tag': version_tag(validation['tag'], tracking), }, {
        'level': level,
        'validation_type': validation_type,
        'error_warning_message': validation['message'],
        'trigger': trigger,
        'trigger_value': validation['trigger_value'],
        'params': params,
        'retrieve': validation['on_retrieve'],
        'update': validation['on_update'],
    })
    for base_quest in validation['questions']:
        try:
            question = Question.objects.get(form_tag=version_tag(base_quest['tag'], tracking))
        except Question.DoesNotExist:
            raise GenerateErrors('Question ' + base_quest['tag'] + ' not found for validation ' + validation['tag'])
        upsert(FormValidationQuestion, {'validation': validation_object, 'question': question}, {})
    validation_object.forms.add(tracking['form'])
    return validation


def update_category(section: SectionSpec, tracking: FormSpecTracking):
    category_tag = version_tag(section['category']['tag'], tracking)
    if section['category']['storage'] is not None:
        check_model = storage_model(section['category']['storage'], tracking)
    else:
        check_model = tracking['main_storage_model']
    try:
        category_type = CategoryType.objects.get(name=section['category']['category_type'])
    except CategoryType.DoesNotExist:
        raise GenerateErrors(
            'Category type ' + section['category']['category_type'] + ' not found for category tag ' + category_tag)
    category = upsert(Category, {'form_tag': category_tag}, {
        'category_type': category_type,
        'description': section['category']['description'],
    })
    for subsection in section['subsections']:
        for question in subsection['questions']:
            try:
                check_model._meta.get_field(question['base_question']['field_name'])
            except FieldDoesNotExist:
                tracking['errors'].append('Question storage field ' + question['base_question']['field_name'] +
                                          ' is not found for question ' + question['base_question']['tag'])
                continue
            try:
                answer_type = AnswerType.objects.get(name=question['base_question']['answer_type'])
            except AnswerType.DoesNotExist:
                raise GenerateErrors(
                    'Answer type ' + question['base_question']['answer_type'] + ' not found for question ' +
                    question['base_question']['tag'])
            question_obj = upsert(Question, {'form_tag': version_tag(question['base_question']['tag'], tracking)}, {
                "answer_type": answer_type,
                "params": question["base_question"]['params'],
                "export_name": question["base_question"]['export_name'],
                "export_params": question["base_question"]['export_params'],
            })
            if question['points'] is not None or question['options'] is not None or question[
                'other_option'] is not None:
                flag_total_questions = []
                if question["total_question"] is not None:
                    for total_question in question["total_question"]:
                        flag_total_questions.append(total_question['tag'])
                flag_points = {
                    'flag_total_questions': flag_total_questions,
                    'points': question['points'],
                    'options': question['options'],
                    'other_option': question['other_option'],
                }
            else:
                flag_points = None
            upsert(QuestionStorage, {
                'question_id': question_obj.id, },
                   {'field_name': question['base_question']['field_name'],
                    })
            upsert(QuestionLayout, {'category_id': category.id, 'question_id': question_obj.id}, {
                'flag_points': flag_points,
            })
            if section['category']['storage'] is None:
                if question['base_question']['tag'] not in tracking['main_tags']:
                    tracking['main_tags'].append(question['base_question']['tag'])
            else:
                if section['category']['tag'] not in tracking['card_tags']:
                    tracking['card_tags'][section['category']['tag']] = []
                tracking['card_tags'][section['category']['tag']].append(question['base_question']['tag'])

    return category


def clean_model(model, version):
    end_match = '.' + version
    remove_qs = model.objects.filter(form_tag__endswith=end_match)
    for to_remove in remove_qs:
        to_remove.delete()


def clean_version(version: str):
    clean_model(FormValidation, version)
    clean_model(ExportImport, version)
    clean_model(Question, version)
    clean_model(Category, version)


class GenerateErrors(Exception):
    def __init__(self, text):
        # Custom attributes
        self.text = text


def generate_form_spec(spec: FormsOfTypeSpec):
    tracking: FormSpecTracking = {
        'form_type': spec['form_type'],
        'version': spec['version'],
        'form': None,
        'main_storage_model': None,
        'main_storage_object': None,
        'main_tags': [],
        'card_tags': {},
        'client_json': {},
        'errors': [],
    }

    try:
        with transaction.atomic():
            clean_version(spec['version'])
            try:
                form_type = FormType.objects.get(name=tracking['form_type'])
            except FormType.DoesNotExist:
                raise GenerateErrors('Form type ' + spec['form_type'] + ' not found')
            for form_spec in spec['form_specs']:
                client_json = generate_form_json(form_spec)
                tracking['client_json'][form_spec['name']] = json.dumps(client_json, indent=4)
                storage = storage_model(form_spec['storage'], tracking)
                if storage is None:
                    continue
                else:
                    tracking['main_storage_model'] = storage
                storage_tag = version_tag(form_spec['storage']['tag'], tracking)
                storage_object = upsert(Storage, {'form_tag': storage_tag}, {
                    'module_name': form_spec['storage']['module_name'],
                    'form_model_name': form_spec['storage']['model_name'],
                })
                tracking['main_storage_object'] = storage_object
                start_time = datetime.datetime(2025,1,1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
                end_time = datetime.datetime(2118,12,31, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
                form = upsert(Form, {'form_name': form_spec['name']},
                              {'form_type': form_type,
                               'storage': storage_object,
                               'start_date': start_time,
                               'end_date': end_time,
                               'version': spec['version'],
                               'client_json': client_json,
                               'use_tag_suffix': True,
                               })
                tracking['form'] = form
                category_index = 1
                for section in form_spec['sections']:
                    category = update_category(section, tracking)
                    if section['category']['storage'] is not None:
                        storage_tag = version_tag(section['category']['storage']['tag'], tracking)
                        category_storage = upsert(Storage, {'form_tag': storage_tag}, {
                            'module_name': section['category']['storage']['module_name'],
                            'form_model_name': section['category']['storage']['model_name'],
                            'parent_storage': tracking['main_storage_object'],
                            'foreign_key_field_parent': section['category']['storage']['parent_field'],
                        })
                    else:
                        category_storage = None
                    upsert(FormCategory, {
                        "form": form,
                        "category": category,
                        "order": category_index,
                        "storage": category_storage,
                    }, {"name": section["name"]})
                for validation in form_spec['validations']:
                    update_validation(validation, tracking)
                if form_spec['export'] is not None:
                    update_google_export(form_spec['export'], tracking)
            if len(tracking['errors']) > 0:
                raise GenerateErrors('Errors occurred')
    except GenerateErrors as e:
        print('errors occurred during generation')

    return tracking
