from datetime import date
from django.db import models
from django.contrib.postgres.fields import JSONField
from .country import Country
from .form import BaseForm, BaseResponse, Question
from .person import Person

# Class to store an instance of the IRF data.
# This should contain data that is common for all IRFs and is not expected to be changed
class Irf(BaseForm):
    irf_number = models.CharField('IRF #:', max_length=20, unique=True)
    number_of_victims = models.PositiveIntegerField('# of victims:', null=True, blank=True)
    location = models.CharField('Location:', max_length=255)
    date_time_of_interception = models.DateTimeField('Date/Time:')
    number_of_traffickers = models.PositiveIntegerField('# of traffickers', null=True, blank=True)
    staff_name = models.CharField('Staff Name:', max_length=255)
    
    drugged_or_drowsy = models.BooleanField('Girl appears drugged or drowsy', default=False)
    who_in_group_husbandwife = models.BooleanField('Husband / Wife', default=False)
    married_in_past_2_weeks = models.BooleanField('Married in the past 2 weeks', default=False).set_weight(15)
    married_in_past_2_8_weeks = models.BooleanField('Married within the past 2-8 weeks', default=False).set_weight(10)
    caught_in_lie = models.BooleanField('Caught in a lie or contradiction', default=False).set_weight(35)
    other_red_flag = models.CharField(max_length=255, blank=True)
    
    where_going_destination = models.CharField('Location:', max_length=126, blank=True)
    
    where_going_job = models.BooleanField('Job', default=False)
    passport_with_broker = models.BooleanField('Passport is with a broker', default=False).set_weight(40)
    job_too_good_to_be_true = models.BooleanField('Job is too good to be true', default=False).set_weight(40)
    not_real_job = models.BooleanField('Not a real job', default=False).set_weight(55)
    couldnt_confirm_job = models.BooleanField('Could not confirm job', default=False).set_weight(10)
    
    where_going_study = models.BooleanField('Study', default=False)
    no_enrollment_docs = models.BooleanField('No documentation of enrollment', default=False).set_weight(15)
    doesnt_know_school_name = models.BooleanField("Does not Know School's Name and location", default=False).set_weight(40)
    no_school_phone = models.BooleanField('No phone number for School', default=False).set_weight(30)
    not_enrolled_in_school = models.BooleanField('Not enrolled in school', default=False).set_weight(60)
    
    where_runaway = models.BooleanField('Runaway', default=False)
    running_away_over_18 = models.BooleanField('Running away from home (18 years or older)', default=False).set_weight(20)
    running_away_under_18 = models.BooleanField('Running away from home (under 18 years old)', default=False).set_weight(50)
    
    reluctant_family_info = models.BooleanField('Reluctant to give family info', default=False).set_weight(10)
    refuses_family_info = models.BooleanField('Will not give family info', default=False).set_weight(35)
    under_18_cant_contact_family = models.BooleanField('No family contact established', default=False).set_weight(50)
    under_18_family_doesnt_know = models.BooleanField("Family doesn't know she is going to India", default=False).set_weight(45)
    under_18_family_unwilling = models.BooleanField('Family unwilling to let her go', default=False).set_weight(60)
    talked_to_family_member = models.CharField(max_length=127, blank=True)
    
    reported_total_red_flags = models.IntegerField('Reported Total Red Flag Points:', null=True, blank=True)
    
    contact_noticed = models.BooleanField('Contact', default=False)
    staff_noticed = models.BooleanField('Staff', default=False)
    staff_who_noticed = models.CharField('Staff who noticed:', max_length=255, blank=True)
    
    trafficking_suspected = models.BooleanField('Trafficking suspected', default=False)
    high_risk_no_evidence = models.BooleanField('High risk of being trafficked, but no evidence of trafficking', default=False)
    trafficker_taken_into_custody = models.CharField(max_length=20, null=True, blank=True)
    
    HOW_SURE_TRAFFICKING_CHOICES = [
        (1, '1 - Not at all sure'),
        (2, '2 - Unsure but suspects it'),
        (3, '3 - Somewhat sure'),
        (4, '4 - Very sure'),
        (5, '5 - Absolutely sure'),
    ]
    how_sure_was_trafficking = models.IntegerField(
        'How sure are you that it was trafficking case?',
        choices=HOW_SURE_TRAFFICKING_CHOICES)

    has_signature = models.BooleanField('Scanned form has signature?', default=False)
    
    def to_str(self, value):
        if value is None:
            return 'None'
        else:
            return str(value)
    
    def __str__(self):
        return self.to_str(self.id) + ":" + self.to_str(self.irf_number) + ", " + self.to_str(self.number_of_victims) + ", " + self.to_str(self.location )+ ", " + self.to_str(self.number_of_traffickers) + ", " + self.to_str(self.staff_name)
    

# Store the responses to questions that are not stored directly in the Irf model.  Includes questions that may
# be changed in the future.  For "Open Response" and "Multi Other Response" where an non-standard answer has
# been provided, the value of answer will be null.
class IrfResponse(BaseResponse):
    parent = models.ForeignKey(Irf)
    
    def to_str(self, value):
        if value is None:
            return 'None'
        else:
            return str(value)
        
    def __str__(self):
        return self.to_str(self.id) + ":" + self.to_str(self.parent.id) + ", " + self.to_str(self.question.id) + ", " + self.to_str(self.value)