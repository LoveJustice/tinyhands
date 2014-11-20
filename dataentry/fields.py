from django.forms import CharField
from dataentry.validators import validate_district, validate_vdc

class DistrictField(CharField):                                                                
    default_validators = [validate_district]

class VDCField(CharField):
    default_validators = [validate_vdc]
