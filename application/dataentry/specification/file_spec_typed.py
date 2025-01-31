from __future__ import annotations  # Needed for recursive types

from typing import List, Self, NotRequired, TypedDict


class StorageSpec(TypedDict):
    tag: str
    module_name: str
    model_name: str
    # parent_storage: NotRequired[str]
    # parent_field: NotRequired[str]
    child_storage_fields: NotRequired[List[StorageFieldSpec]]


# Maybe delete this and use parent_storage/parent_field
class StorageFieldSpec(TypedDict):
    field_name: str
    storage: StorageSpec


class BaseQuestionSpec(TypedDict):
    tag: str
    answer_type: str
    field_name: str
    export_name: str
    params: NotRequired[str]  # Python 3.11+
    export_params: NotRequired[str]


class CategorySpec(TypedDict):
    tag: str
    category_type: str
    description: str
    storage: NotRequired[StorageSpec]  # Could also use StorageSpec | None to be clearer


class OptionsAndPointsSpec(TypedDict):
    value: str
    points: int


class QuestionSpec(TypedDict):
    base_question: BaseQuestionSpec
    label: str
    entry_type: str
    span: NotRequired[int]
    total: NotRequired[BaseQuestionSpec]
    points: NotRequired[int]
    options: NotRequired[List[OptionsAndPointsSpec]]
    other_option: NotRequired[OptionsAndPointsSpec]


class SubSectionSpec(TypedDict):
    title: str
    key: str
    side: str
    questions: List[QuestionSpec]


class SectionSpec(TypedDict):
    name: str
    section_type: str
    category: CategorySpec
    subsections: List[SubSectionSpec]


class ValidationSpec(TypedDict):
    tag: str
    level: str
    validation_type: str
    message: str
    questions: List[BaseQuestionSpec]
    trigger: NotRequired[BaseQuestionSpec]
    trigger_value: NotRequired[str]
    params: NotRequired[str]
    on_retrieve: NotRequired[bool]  # NOTE -> Default to False
    on_update: NotRequired[bool]  # NOTE -> Default to True


class GoogleExportCardSpec(TypedDict):
    category: CategorySpec
    prefix: str
    max_instances: int
    index_field_name: str


# ??????
# class GoogleExportFieldSpec(TypedDict):
#     def __init__(None,
#                  arguments_json: str = None):
#         field_name
#         answer_type
#         export_name
#         card
#         arguments_json


class GoogleExportSpec(TypedDict):
    tag: str
    module_name: str
    class_name: str
    spreadsheet_name: str
    sheet_name: str
    key_field_name: str
    cards: List[GoogleExportCardSpec]
    # fields: List[GoogleExportFieldSpec]
    supress_warnings: NotRequired[bool]  # NOTE -> Default to True


class FormSpec(TypedDict):
    name: str
    storage: StorageSpec
    version: str
    sections: List[SectionSpec]
    validations: NotRequired[List[ValidationSpec]]
    # export: NotRequired[GoogleExportFieldSpec]


class FormsOfTypeSpec(TypedDict):
    form_type: str
    form_specs: List[FormSpec]