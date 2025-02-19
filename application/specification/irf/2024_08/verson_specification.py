from specification.form_spec import FormsOfTypeSpec
from .example import irf_example

version_specification: FormsOfTypeSpec = {
    'form_type': 'IRF',
    'version': '2024.8',
    'form_specs': [irf_example],
}
