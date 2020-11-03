from django.db import models

from accounts.models import Account

from .person import Person
from .form import BaseCard
from .form import BaseForm

class LegalCase(BaseForm):
    legal_case_number = models.CharField('LC #:', max_length=20, unique=True)
    police_case = models.CharField(max_length=255, null=True)
    court_case = models.CharField(max_length=255, null=True)
    charge_sheet_date = models.DateField(null=True)
    case_type = models.CharField(max_length=255, null=True)
    date_last_contacted = models.DateField(null=True)
    comment = models.TextField(blank=True)
    appealed = models.BooleanField(default=False)
    lawyer_name = models.CharField(max_length=255, null=True)
    lawyer_phone = models.CharField(max_length=255, null=True)
    
    def get_key(self):
        return self.legal_case_number
    
    def get_form_type_name(self):
        return 'LEGAL_CASE'
    
    @staticmethod
    def key_field_name():
        return 'legal_case_number'
    
class LegalCaseSuspect(BaseCard):
    legal_case = models.ForeignKey(LegalCase, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, null=True)
    named_on_charge_sheet = models.BooleanField(default=False)
    arrest_date = models.DateField(null=True)
    arrest_status = models.CharField(max_length=255, null=True)
    verdict = models.CharField(max_length=255, null=True)
    verdict_date = models.DateField(null=True)
    imprisonment_years = models.PositiveIntegerField(null=True, blank=True)
    imprisonment_months = models.PositiveIntegerField(null=True, blank=True)
    imprisonment_days = models.PositiveIntegerField(null=True, blank=True)
    imprisonment_total_days = models.PositiveIntegerField(null=True, blank=True)
    fine_amount = models.CharField(max_length=255, null=True)
    
    
    def set_parent(self, the_parent):
        self.legal_case = the_parent

class LegalCaseVictim(BaseCard):
    legal_case = models.ForeignKey(LegalCase, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, null=True)
    alternate_phone = models.CharField(max_length=255, null=True)
    last_contact_date = models.DateField(null=True)
    last_attempted_contact_date = models.DateField(null=True)
    victim_status = models.CharField(max_length=255, null=True)
    
    def set_parent(self, the_parent):
        self.legal_case = the_parent

class LegalCaseAttachment(BaseCard):
    legal_case = models.ForeignKey(LegalCase, on_delete=models.CASCADE)
    attachment_number = models.PositiveIntegerField(null=True, blank=True)
    description = models.CharField(max_length=126, null=True)
    attachment = models.FileField('Attach scanned copy of form (pdf or image)', upload_to='scanned_irf_forms')
    private_card = models.BooleanField(default=True)
    option = models.CharField(max_length=126, null=True)
    
    def set_parent(self, the_parent):
        self.legal_case = the_parent
    
    def is_private(self):
        return self.private_card