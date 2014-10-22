from django.core.exceptions import ValidationError, ObjectDoesNotExist
from dataentry.models import District, VDC

def validate_district(value):
    try:
        district = District.objects.get(name=value)
    except ObjectDoesNotExist:
        raise ValidationError("%s is not a valid district" % value)

