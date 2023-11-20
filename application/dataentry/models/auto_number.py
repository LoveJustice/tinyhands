import re
from django.db import models
from django.db.models import Q
from django.db.models import Max
from dataentry.models import BorderStation, FormType
from django.core.exceptions import ObjectDoesNotExist

class AutoNumber(models.Model):
    station = models.ForeignKey(BorderStation)
    form_type = models.ForeignKey(FormType)
    last_allocated = models.PositiveIntegerField()
    
    @staticmethod
    def get_next_number(station, form):
        form_type = form.form_type
        try:
            auto_number = AutoNumber.objects.get(station=station, form_type=form_type)
            auto_number.last_allocated += 1
            auto_number.save()
        except ObjectDoesNotExist:
            storage_class = form.storage.get_form_storage_class()
            q_filter = Q(**{storage_class.key_field_name() + "__startswith": station.station_code})
            result = storage_class.objects.filter(q_filter).aggregate(Max(storage_class.key_field_name()))
            if storage_class.key_field_name() + '__max' in result and result[storage_class.key_field_name() + '__max'] is not None:
                parts = result[storage_class.key_field_name() + '__max'].split('.')
                tmp = parts[0][len(station.station_code):]
                tmp = re.sub('[^0-9]','', tmp)
                current_max = int(tmp)
            else:
                current_max = 0
            auto_number = AutoNumber()
            auto_number.station = station
            auto_number.form_type = form_type
            auto_number.last_allocated = current_max + 1
            auto_number.save()
        
        tmp = str(auto_number.last_allocated)
        if auto_number.last_allocated < 10:
            tmp = '00' + tmp
        elif auto_number.last_allocated < 100:
            tmp = '0' + tmp
        
        form_number = station.station_code + tmp
        if form_type.name == 'CIF':
            form_number += '.1'
        
        return form_number
    
    @staticmethod
    def check_number(station, form, form_number):
        form_type = form.form_type
        try:
            auto_number = AutoNumber.objects.get(station=station, form_type=form_type)
            last_allocated = auto_number.last_allocated
        except ObjectDoesNotExist:
            last_allocated = -1
        
        parts = form_number.split('.')
        tmp = parts[0][len(station.station_code):]
        tmp = re.sub('[^0-9]','', tmp)
        nbr = int(tmp)
        if nbr <= last_allocated:
            return True
        
        return False
        
        
