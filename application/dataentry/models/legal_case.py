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
    appealed = models.BooleanField(default=False)
    lawyer_name = models.CharField(max_length=255, null=True)
    lawyer_phone = models.CharField(max_length=255, null=True)
    source = models.CharField(max_length=255, null=True)
    missing_data_count = models.PositiveIntegerField(null=True, blank=True)
    
    def get_key(self):
        return self.legal_case_number
    
    def get_form_type_name(self):
        return 'LEGAL_CASE'
    
    def get_form_date(self):
        return self.charge_sheet_date
    
    @staticmethod
    def key_field_name():
        return 'legal_case_number'

class LegalCaseTimeline(BaseCard):
    legal_case = models.ForeignKey(LegalCase, on_delete=models.CASCADE)
    comment_date = models.DateField()
    comment = models.TextField()
    added_by = models.CharField(max_length=255, null=True)
    date_added = models.DateField(auto_now_add=True)
    date_removed = models.DateField(null=True)
    
    def set_parent(self, the_parent):
        self.legal_case = the_parent
    
class LegalCaseSuspect(BaseCard):
    legal_case = models.ForeignKey(LegalCase, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, null=True)
    named_on_charge_sheet = models.CharField(max_length=255, null=True)
    arrest_date = models.DateField(null=True)
    arrest_status = models.CharField(max_length=255, null=True)
    verdict = models.CharField(max_length=255, null=True)
    named_in_verdict = models.CharField(max_length=255, null=True)
    verdict_date = models.DateField(null=True)
    imprisonment_years = models.PositiveIntegerField(null=True, blank=True)
    imprisonment_months = models.PositiveIntegerField(null=True, blank=True)
    imprisonment_days = models.PositiveIntegerField(null=True, blank=True)
    imprisonment_total_days = models.PositiveIntegerField(null=True, blank=True)
    fine_amount = models.PositiveIntegerField(null=True, blank=True)
    fine_currency = models.CharField(max_length=255, null=True)
    
    
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