from __future__ import annotations  # Needed for recursive types

from typing import List, TypedDict


class StorageSpec(TypedDict):
    tag: str
    module_name: str
    model_name: str
    parent_storage: StorageSpec | None
    parent_field: str | None


class BaseQuestionSpec(TypedDict):
    tag: str
    answer_type: str
    field_name: str
    export_name: str
    params: str | None
    export_params: str | None


class CategorySpec(TypedDict):
    tag: str
    category_type: str
    description: str
    storage: StorageSpec | None


class OptionsAndPointsSpec(TypedDict):
    value: str
    points: int


class QuestionSpec(TypedDict):
    base_question: BaseQuestionSpec
    label: str
    entry_type: str
    span: int | None
    total: BaseQuestionSpec | None
    points: int | None
    options: List[OptionsAndPointsSpec] | None
    other_option: OptionsAndPointsSpec | None


class SubSectionSpec(TypedDict):
    title: str
    key: str
    side: str
    questions: List[QuestionSpec]


class SectionSpec(TypedDict):
    name: str
    category: CategorySpec
    subsections: List[SubSectionSpec]


class ValidationSpec(TypedDict):
    tag: str
    level: str
    validation_type: str
    message: str
    questions: List[BaseQuestionSpec]
    trigger: BaseQuestionSpec | None
    trigger_value: str | None
    params: str | None
    on_retrieve: bool
    on_update: bool


class GoogleExportCardSpec(TypedDict):
    category: CategorySpec
    prefix: str
    max_instances: int
    index_field_name: str


class GoogleExportFieldSpec(TypedDict):
    field_name: str
    answer_type: str
    export_name: str
    card: GoogleExportCardSpec | None
    argument_json: str | None


class GoogleExportSpec(TypedDict):
    tag: str
    module_name: str
    class_name: str
    spreadsheet_name: str
    sheet_name: str
    key_field_name: str
    cards: List[GoogleExportCardSpec]
    fields: List[GoogleExportFieldSpec]
    suppress_warnings: bool


class FormSpec(TypedDict):
    name: str
    storage: StorageSpec
    sections: List[SectionSpec]
    validations: List[ValidationSpec]
    export: GoogleExportSpec | None


class FormsOfTypeSpec(TypedDict):
    form_type: str
    version: str
    form_specs: List[FormSpec]

