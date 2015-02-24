from django.forms import CharField, IntegerField
from dataentry.validators import validate_district, validate_vdc

class DistrictField(CharField):                                                                
    default_validators = [validate_district]

class VDCField(CharField):
    default_validators = [validate_vdc]

class PersonIdField(IntegerField):
    def __init__(self):
        super(PersonIdField, self).__init__(required=False)