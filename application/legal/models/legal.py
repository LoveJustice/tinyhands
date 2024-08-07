from django.db import models

from dataentry.models import BaseCard, BaseForm, Country
from dataentry.models import Incident, Suspect, VdfCommon

class LegalCharge(BaseForm):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE)
    legal_charge_number = models.CharField(max_length=20, unique=True)
    source = models.CharField(max_length=127, null=True)
    location = models.CharField(max_length=255, null=True)
    charge_sheet_date = models.DateField(null=True)
    police_case = models.CharField(max_length=127, null=True)
    human_trafficking = models.CharField(max_length=255, null=True)
    case_summary = models.TextField(null=True)
    date_last_contacted = models.DateField(null=True)
    missing_data_count = models.PositiveIntegerField(null=True, blank=True)
    
    def get_key(self):
        return self.incident.incident_number
    
    def get_form_type_name(self):
        return 'LEGAL_CASE'
    
    def get_form_date(self):
        return self.charge_sheet_date
    
    @staticmethod
    def key_field_name():
        return 'incident__incident_number'

class CourtCase(BaseCard):
    legal_charge = models.ForeignKey(LegalCharge, on_delete=models.CASCADE)
    sequence_number = models.PositiveIntegerField()     # assigned by the client when adding court case
    court_case = models.CharField(max_length=127, null=True)
    district_court = models.CharField(max_length=127, null=True)
    status = models.CharField(max_length=127, null=True)
    charges = models.CharField(max_length=255, null=True)
    specific_code_law = models.TextField(null=True)
    
    def set_parent(self, the_parent):
        self.legal_charge = the_parent
    
class LegalChargeSuspect(BaseCard):
    legal_charge = models.ForeignKey(LegalCharge, on_delete=models.CASCADE)
    sf = models.ForeignKey(Suspect, on_delete=models.CASCADE)
    arrested = models.CharField(max_length=255, null=True)
    arrest_status = models.CharField(max_length=255, null=True)
    named_on_charge_sheet = models.CharField(max_length=127, null=True)
    arrest_date = models.DateField(null=True)
    arrest_submitted_date = models.DateField(null=True)
    court_cases = models.CharField(max_length=255, null=True) # delimited list of CourtCase sequence numbers
    verified_attachment = models.CharField(max_length=127, null=True)
    taken_into_custody = models.CharField(max_length=127, null=True)
    charged_with_crime = models.CharField(max_length=127, null=True)
    how_do_you_know = models.TextField(null=True)
    verified_by = models.CharField(max_length=127, null=True)
    verified_date = models.DateField(null=True)
    
    
    
    def set_parent(self, the_parent):
        self.legal_charge = the_parent

# Current framework will not support storing a foreign key to CourtCase or LegalChargeSuspect.
# We can use the sequence number from the court case to identify the corresponding CourtCase
# and the SF reference to identify the LegalChargeSuspect  
class LegalChargeSuspectCharge(BaseCard):
    legal_charge = models.ForeignKey(LegalCharge, on_delete=models.CASCADE)
    sf = models.ForeignKey(Suspect, on_delete=models.CASCADE)
    court_case_sequence = models.PositiveIntegerField()
    charge = models.CharField(max_length=127, null=True) 
    legal_status = models.CharField(max_length=127, null=True)    
    verdict = models.CharField(max_length=127, null=True)
    sentence_attached = models.CharField(max_length=127, null=True)
    verdict_date = models.DateField(null=True)
    verdict_submitted_date = models.DateField(null=True)
    imprisonment_years = models.PositiveIntegerField(null=True, blank=True)
    imprisonment_days = models.PositiveIntegerField(null=True, blank=True)
    imprisonment_total_days = models.PositiveIntegerField(null=True, blank=True)
    fine_amount = models.PositiveIntegerField(null=True, blank=True)
    fine_currency = models.CharField(max_length=255, null=True)
    
    def set_parent(self, the_parent):
        self.legal_charge = the_parent

class LegalChargeVictim(BaseCard):
    legal_charge = models.ForeignKey(LegalCharge, on_delete=models.CASCADE)
    pvf= models.ForeignKey(VdfCommon, on_delete=models.CASCADE)
    alternate_phone = models.CharField(max_length=255, null=True)
    last_contact_date = models.DateField(null=True)
    last_attempted_contact_date = models.DateField(null=True)
    victim_status = models.TextField(null=True)
    court_cases = models.CharField(max_length=255, null=True) # delimited list of CourtCase sequence numbers
    
    def set_parent(self, the_parent):
        self.legal_charge = the_parent

class LegalChargeTimeline(BaseCard):  # Same as current
    legal_charge = models.ForeignKey(LegalCharge, on_delete=models.CASCADE)
    court_case_sequence = models.PositiveIntegerField()
    comment_date = models.DateField()
    comment = models.TextField()
    added_by = models.CharField(max_length=255, null=True)
    date_added = models.DateField(auto_now_add=True)
    date_removed = models.DateField(null=True)
    
    def set_parent(self, the_parent):
        self.legal_charge = the_parent

class LegalChargeAttachment(BaseCard):  # Same as current
    legal_charge = models.ForeignKey(LegalCharge, on_delete=models.CASCADE)
    attachment_number = models.PositiveIntegerField(null=True, blank=True)
    description = models.CharField(max_length=126, null=True)
    attachment = models.FileField('Attach scanned copy of form (pdf or image)', upload_to='legal_case_attachments')
    private_card = models.BooleanField(default=True)
    option = models.CharField(max_length=126, null=True)
    
    def set_parent(self, the_parent):
        self.legal_charge = the_parent
    
    def is_private(self):
        return self.private_card

class LegalChargeCountrySpecific(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    charge = models.CharField(max_length=127, null=True)
    