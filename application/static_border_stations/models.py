import datetime
from django.db import models
from dataentry.models import BorderStation


class NullableEmailField(models.EmailField):
    description = "EmailField that stores NULL but returns ''"

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return ''
        return value

    def to_python(self, value):
        if isinstance(value, models.EmailField):
            return value
        return value or ''

    def get_prep_value(self, value):
        return value or None


class Person(models.Model):
    email = NullableEmailField(blank=True, null=True, default=None, unique=False)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    position = models.CharField(max_length=255, blank=True, null=True)
    receives_money_distribution_form = models.BooleanField(default=False)
    border_station = models.ForeignKey(BorderStation, null=True)

    class Meta:
        abstract = True

    @property
    def full_name(self):
        return self.first_name + ' ' + self.last_name
    
    def get_country_id(self):
        if self.border_station is None or self.border_station.operating_country is None:
            return None
        return self.border_station.operating_country.id
    
    def get_border_station_id(self):
        if self.border_station is None:
            return None
        return self.border_station.id

    def __str__(self):
        return self.full_name
    
    def set_parent(self, the_parent):
        self.border_station = the_parent
    
    def is_private(self):
        return False

class Staff(Person):
    class Meta:
        abstract = False
    first_date = models.DateField(default=datetime.datetime.now)
    last_date = models.DateField(null=True)
        

class CommitteeMember(Person):
    class Meta:
        abstract = False

class Location(models.Model):
    name = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    border_station = models.ForeignKey(BorderStation, null=True)
    location_type = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    
    def get_country_id(self):
        if self.border_station is None or self.border_station.operating_country is None:
            return None
        return self.border_station.operating_country.id
    
    def get_border_station_id(self):
        if self.border_station is None:
            return None
        return self.border_station.id
    
    def set_parent(self, the_parent):
        self.border_station = the_parent
    
    def is_private(self):
        return False
