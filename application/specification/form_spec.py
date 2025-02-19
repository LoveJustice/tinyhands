from __future__ import annotations  # Needed for recursive types

from typing import List, Literal, TypedDict


class StorageSpec(TypedDict):
    tag: str
    module_name: str
    model_name: str
    parent_storage: StorageSpec | None
    parent_field: str | None


AnswerType = Literal[
    "String", "Integer", "Float", "RadioButton", "Dropdown", "Checkbox", "Address", "Phone", "Date", "DateTime",
    "ArcGisAddress", "Image", "PromptOnly", "Person", "MultiReference"]


class BaseQuestionSpec(TypedDict):
    tag: str
    answer_type: AnswerType
    field_name: str
    export_name: str
    params: str | None
    export_params: str | None


CategoryType = Literal["grid", "card"]


class CategorySpec(TypedDict):
    tag: str
    category_type: CategoryType
    description: str
    storage: StorageSpec | None


class OptionsAndPointsSpec(TypedDict):
    value: str
    points: int


EntryType = Literal["text", "number", "checkbox", "sum"]


class QuestionSpec(TypedDict):
    base_question: BaseQuestionSpec
    label: str
    entry_type: EntryType
    span: int | None
    total_question: List[BaseQuestionSpec] | None
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
    params: dict[str, any] | None
    on_retrieve: bool
    on_update: bool


class GoogleExportCardSpec(TypedDict):
    category: CategorySpec
    prefix: str
    max_instances: int
    index_field_name: str | None


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
