from django.forms import CharField
from dataentry.validators import validate_district, validate_vdc

class DistrictField(CharField):
    def __init__(self, *args, **kwargs):
        super(DistrictField, self).__init__(*args, **kwargs)
    default_validators = [validate_district]

class VDCField(CharField):
    def __init__(self, *args, **kwargs):
        super(VDCField, self).__init__(*args, **kwargs)
    default_validators = [validate_vdc]
