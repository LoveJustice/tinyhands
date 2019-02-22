from django.db import models

from .cif_core import CifAttachment, CifCore, LocationBoxCore, PersonBoxCore, PotentialVictimCore, TransporationCore, VehicleBoxCore

class CifNepal(CifCore):
    # Recruitment
    broker_relation = models.CharField(max_length=126, null=True)
    expected_earning_currency = models.CharField(max_length=126, null=True)

    # Travel
    purpose_for_leaving_job_massage = models.BooleanField( default=False)
    
    #Legal
    case_exploration_under_16_separated = models.BooleanField( default=False)
    case_exploration_under_18_sent_job = models.BooleanField( default=False)
    case_exploration_under_16_sexually_abused = models.BooleanField( default=False)
    case_exploration_female_18_30_gulf_country = models.BooleanField( default=False)
    case_exploration_detained_against_will = models.BooleanField( default=False)
    case_exploration_abused = models.BooleanField( default=False)

class PotentialVictimNepal(PotentialVictimCore):
    cif = models.ForeignKey(CifNepal)
    
    def set_parent(self, the_parent):
        self.cif = the_parent

class TransporationNepal(TransporationCore):
    cif = models.ForeignKey(CifNepal)
    
    def set_parent(self, the_parent):
        self.cif = the_parent

class PersonBoxNepal(PersonBoxCore):
    cif = models.ForeignKey(CifNepal)
    
    def set_parent(self, the_parent):
        self.cif = the_parent

class LocationBoxNepal(LocationBoxCore):
    cif = models.ForeignKey(CifNepal)
    
    def set_parent(self, the_parent):
        self.cif = the_parent

class VehicleBoxNepal(VehicleBoxCore):
    cif = models.ForeignKey(CifNepal)
    
    def set_parent(self, the_parent):
        self.cif = the_parent

class CifAttachmentNepal(CifAttachment):
    cif = models.ForeignKey(CifNepal)
    
    def set_parent(self, the_parent):
        self.cif = the_parent
    


