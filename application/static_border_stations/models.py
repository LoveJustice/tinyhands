from datetime import date
from django.db import models
from dataentry.models import BorderStation
from django.core.exceptions import ObjectDoesNotExist

class NullableEmailField(models.EmailField):
    description = "EmailField that stores NULL but returns ''"

    def from_db_value(self, value, expression, connection):
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
    email = email = NullableEmailField(blank=True, null=True, default=None, unique=False)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    position = models.CharField(max_length=255, blank=True, null=True)
    receives_money_distribution_form = models.BooleanField(default=False)
    border_station = models.ForeignKey(BorderStation, null=True, on_delete=models.CASCADE)
    country = models.ForeignKey('dataentry.Country', null=True, on_delete=models.CASCADE)

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
    first_date = models.DateField(default=date.today)
    last_date = models.DateField(null=True)
    
    general_staff = '__general_staff'
    
    @staticmethod 
    def get_or_create_general_staff(border_station):
        try:
            general = Staff.objects.get(border_station=border_station, last_name=Staff.general_staff)
        except ObjectDoesNotExist:
            general = Staff()
            general.last_name = Staff.general_staff
            general.border_station = border_station
            general.first_date = date.today()
            general.last_date = general.first_date
            general.save()
        
        return general

class CommitteeMember(Person):
    class Meta:
        abstract = False

class Location(models.Model):
    name = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    border_station = models.ForeignKey(BorderStation, null=True, on_delete=models.CASCADE)
    location_type = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    
    other_name = '__Other'
    leave_name = 'Leave'
    
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
    
    @staticmethod
    def get_or_create_other_location(border_station):
        try:
            location = Location.objects.get(border_station=border_station, name=Location.other_name)
        except ObjectDoesNotExist:
            location = Location()
            location.name = Location.other_name
            location.border_station = border_station
            location.active = False
            location.location_type = 'monitoring'
            location.save()
        
        return location
    
    @staticmethod
    def get_or_create_leave_location(border_station):
        try:
            location = Location.objects.get(border_station=border_station, name=Location.leave_name)
        except ObjectDoesNotExist:
            location = Location()
            location.name = Location.leave_name
            location.border_station = border_station
            location.active = False
            location.location_type = 'monitoring'
            location.save()
        
        return location
  
class WorksOnProject(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    border_station = models.ForeignKey(BorderStation, on_delete=models.CASCADE)
    work_percent = models.PositiveIntegerField()
    
    class Meta:
       unique_together = ("staff", "border_station")
    
    def set_parent(self, parent):
        self.staff = parent

class StaffProject(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    border_station = models.ForeignKey(BorderStation, on_delete=models.CASCADE)
    coordinator = models.CharField(max_length=127, blank=True)
    receives_money_distribution_form = models.BooleanField(default=False)
    
    class Meta:
       unique_together = ("staff", "border_station")
    
    def set_parent(self, parent):
        self.staff = parent
