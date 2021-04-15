from django.db import models
from .country import Country


class BorderStation(models.Model):
    station_code = models.CharField(max_length=3, unique=True)
    station_name = models.CharField(max_length=100)
    date_established = models.DateField(null=True)
    has_shelter = models.BooleanField(default=False)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    open = models.BooleanField(default=True)
    operating_country = models.ForeignKey(Country, models.SET_NULL, null=True, blank=True)
    time_zone = models.CharField(max_length=127, blank=False)
    non_transit = models.BooleanField(default=False)
    auto_number= models.CharField(max_length=127, null=True)
    
    def get_country_id(self):
        if self.operating_country is None:
            return None
        return self.operating_country.id
    
    
    def get_border_station_id(self):
        return self.id
    
    def get_key(self):
        return station_code
    
    def pre_save(self, form_data):
        pass
    
    def post_save(self, form_data):
        pass

    def __str__(self):
        return self.station_name
