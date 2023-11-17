from django.db import models
from datetime import date

from accounts.models import Account

class MasterPerson (models.Model):
    GENDER_CHOICES = [('M', 'm'), ('F', 'f')]

    full_name = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=4, choices=GENDER_CHOICES, blank=True)
    birthdate = models.DateField(null=True)
    estimated_birthdate = models.BooleanField('Estimated birthdate', default=False)
    nationality = models.CharField(max_length=127, blank=True, default='')
    appearance = models.TextField('Appearance', blank=True)
    notes = models.TextField('Notes', blank=True)
    active = models.BooleanField(default=True)

    # invoked when new person is linked to the master person
    def update(self, person):
        if self.full_name == '' or self.full_name is None:
            self.full_name = person.full_name
        if self.gender == '' :
            self.gender = person.gender
        if self.birthdate is None:
            if person.birthdate is not None:
                self.birthdate = person.birthdate
                self.estimated_birthdate = False
            elif person.estimated_birthdate is not None:
                self.birthdate = person.estimated_birthdate
                self.estimated_birthdate = True
        if self.nationality == '':
            self.nationality = person.nationality
    
    @property
    def age(self):
        if self.birthdate is None:
            years = None
        else:
            today = date.today()
            years = today.year - self.birthdate.year
            if today.month < self.birthdate.month or (today.month == self.birthdate.month and today.day < self.birthdate.day):
                years -= 1
        
        return years

class AddressType (models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    
class PersonAddress (models.Model):
    master_person = models.ForeignKey(MasterPerson, on_delete=models.CASCADE)
    address = models.JSONField(null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    address_notes = models.TextField('Address Notes', blank=True)
    address_verified = models.BooleanField('Address Verified', default=False)
    address_type = models.ForeignKey(AddressType, null=True, on_delete=models.SET_NULL)

class PhoneType (models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    
class PersonPhone (models.Model):
    master_person = models.ForeignKey(MasterPerson, on_delete=models.CASCADE)
    number = models.CharField(max_length=255, blank=True)
    phone_verified = models.BooleanField('Phone Verified', default=False)
    phone_type = models.ForeignKey(PhoneType, null=True, on_delete=models.SET_NULL)
    
class SocialMediaType (models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)

class PersonSocialMedia (models.Model):
    master_person = models.ForeignKey(MasterPerson, on_delete=models.CASCADE)
    social_media = models.CharField(max_length=1024, blank=True)
    social_media_verified = models.BooleanField('Social Media Verified', default=False)
    social_media_type = models.ForeignKey(SocialMediaType, null=True, on_delete=models.SET_NULL)

class DocumentType (models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)

class PersonDocument (models.Model):
    master_person = models.ForeignKey(MasterPerson, on_delete=models.CASCADE)
    file_location = models.FileField('Attach scanned copy of form (pdf or image)', upload_to='person_documents')
    document_type = models.ForeignKey(DocumentType, null=True, on_delete=models.SET_NULL)

class MatchType (models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    
class PersonMatch (models.Model):
    match_type = models.ForeignKey(MatchType, on_delete=models.CASCADE)
    master1 = models.ForeignKey(MasterPerson, related_name='master1', on_delete=models.CASCADE)
    master2 = models.ForeignKey(MasterPerson, related_name='master2', on_delete=models.CASCADE)
    notes = models.TextField('Notes', blank=True)
    match_date = models.DateField(auto_now=True)
    matched_by = models.ForeignKey(Account, null=True, on_delete=models.SET_NULL)
    match_results = models.JSONField(null=True)
    