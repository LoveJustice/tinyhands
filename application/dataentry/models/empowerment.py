from django.db import models

from .border_station import BorderStation

class Empowerment(models.Model):
    station = models.ForeignKey(BorderStation)
    date_time_entered_into_system = models.DateTimeField(auto_now_add=True)
    date_time_last_updated = models.DateTimeField(auto_now=True)
    
    full_name = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=4, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    vdf_number = models.CharField(max_length=255, null=True, blank=True)
    
    pre_emp_usd = models.DecimalField(max_digits=17, decimal_places=2)
    pre_emp_local = models.CharField(max_length=255, null=True, blank=True)
    post_emp_usd = models.DecimalField(max_digits=17, decimal_places=2)
    post_emp_local = models.CharField(max_length=255, null=True, blank=True)
    lines_crossed = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    @property
    def levels(self):
        day_levels = [1,1.9,3.2,5.5]
        if self.station is not None:
            options = self.station.operating_country.options
            if options is not None and 'empowerment_levels' in options:
                day_levels = options['empowerment_levels']
        
        return day_levels;