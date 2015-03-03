from django.db import models
from dataentry.models import BorderStation
'''
class BorderStationBudgetCalculationForm(models.Model):
    form_entered_by = models.ForeignKey(Account)
    date_created = models.DateTimeField()
    
    form_updated_by = models.ForeignKey(Account)
    date_updated = models.DateTimeField()
    
    name = models.ForeignKey(BorderStation,null=False)
    
    communication_chair = models.BooleanField('Chair', default=False)
    communication_manager =  models.BooleanField('Manager', default=False)
    communication_number_of_staff_with_walkie_talkies = models.PositiveIntegerField('# of staff with walkie-talkies', null=True, blank=True)
    communication_each_staff = models.PositiveIntegerField('each staff', null=True, blank=True)
    
    travel_chair_with_bike = models.BooleanField('Chair with Bike', default=False)
    travel_manager_with_bike = models.BooleanField('Chair with Bike', default=False)
    travel_number_of_staff_using_bikes = models.PositiveIntegerField('# of staff using bikes', null=True, blank=True)
    travel_last_months_expense_for_sending_girls_home = models.FloatField()
    travel_motorbike =  models.BooleanField('Motorbike', default=False)
    travel_other_expenses = models.FloatField()
    
    administration_number_of_intercepts_last_month = models.PositiveIntegerField('# of intercepts last month', null=True, blank=True)
    administration_number_of_meetings_per_month = models.PositiveIntegerField('# of meetings per month', null=True, blank=True)
    administration_booth = models.BooleanField('Booth', default=False)
    administration_registration = models.BooleanField('Registration', default=False)
    
    medical_last_months_expense = models.FloatField()
    
    miscellaneous_number_of_intercepts_last_month = models.PositiveIntegerField('# of intercepts last month', null=True, blank=True)
    
    shelter_rent = models.FloatField()
    shelter_water = models.FloatField()
    shelter_electricity = models.FloatField()
    #shelter_shelter_startup = models.BooleanField('Shelter Startup', default=False) More work here!
    
    food_and_gas_number_of_intercepted_girls = models.PositiveIntegerField('# of intercepted girls', null=True, blank=True)
    food_and_gas_number_of_limbo_girls = models.PositiveIntegerField('# of limbo girls', null=True, blank=True)
    food_and_gas_number_of_days = models.PositiveIntegerField('# of days', null=True, blank=True)
    
    awareness_contact_cards = models.BooleanField('Contact Cards', default=False)
    awareness_awareness_party = models.FloatField()
    awareness_sign_boards = models.FloatField()
    awareness_other = models.FloatField()
'''