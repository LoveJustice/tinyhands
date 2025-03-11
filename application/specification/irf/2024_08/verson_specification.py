from specification.form_spec import FormsOfTypeSpec
from .argentina import irf_argentina
from .bangladesh import irf_bangladesh
from .benin import irf_benin
from .burkina_faso import irf_burkina_faso
from .burundi import irf_burundi
from .cambodia import irf_cambodia
from .ecuador import irf_ecuador
from .ethiopia import irf_ethiopia
from .ghana import irf_ghana
from .india import irf_india
from .indianetwork import irf_indianetwork
from .indonesia import irf_indonesia
from .kenya import irf_kenya
from .lesotho import irf_lesotho
from .liberia import irf_liberia
from .malawi import irf_malawi
from .mozambique import irf_mozambique
from .namibia import irf_namibia
from .nepal import irf_nepal
from .philippines import irf_philippines
from .rwanda import irf_rwanda
from .sierra_leone import irf_sierra_leone
from .south_africa import irf_south_africa
from .tanzania import irf_tanzania
from .uganda import irf_uganda
from .usa import irf_usa
from .zambia import irf_zambia
from .zimbabwe import irf_zimbabwe

version_specification: FormsOfTypeSpec = {
    'form_type': 'IRF',
    'version': '2024.8',
    'form_specs': [
        irf_argentina,
        irf_bangladesh,
        irf_benin,
        irf_burkina_faso,
        irf_burundi,
        irf_cambodia,
        irf_ecuador,
        irf_ethiopia,
        irf_ghana,
        irf_india,
        irf_indianetwork,
        irf_indonesia,
        irf_kenya,
        irf_lesotho,
        irf_liberia,
        irf_malawi,
        irf_mozambique,
        irf_namibia,
        irf_nepal,
        irf_philippines,
        irf_rwanda,
        irf_sierra_leone,
        irf_south_africa,
        irf_tanzania,
        irf_uganda,
        irf_usa,
        irf_zambia,
        irf_zimbabwe,
    ]
}
