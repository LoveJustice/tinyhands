from django.core.exceptions import ValidationError
from django.forms import CharField

from .models import District, VDC, BorderStation


class DistrictField(CharField):
    def validate(self, value):
        super(DistrictField, self).validate(value)
        # Note that we don't have to deal with whether a field is required or not, as the
        # superclass takes care of it for us. If we do have a value, the associated
        # District must exist.
        if value and not District.objects.filter(name=value).exists():
            raise ValidationError("%(value)s is not a valid district.",
                                  params={'value': value})


class VDCField(CharField):
    def validate(self, value):
        super(VDCField, self).validate(value)
        # See comment above.
        if value and not VDC.objects.filter(name=value).exists():
            raise ValidationError("%(value)s is not a valid VDC.",
                                  params={'value': value})


class FormNumberField(CharField):
    def validate(self, value):
        super(FormNumberField, self).validate(value)

        border_station_code = value[:3]
        if len(border_station_code) != 3:
            raise ValidationError('Invalid form number: must have three-character Border Station code.')
        if not BorderStation.objects.filter(station_code=border_station_code).exists():
            raise ValidationError('Invalid form number: invalid Border Station code.')

        form_number = value[3:]
        if len(form_number) == 0:
            raise ValidationError('Invalid form number: add a number after the Border Station code.')
