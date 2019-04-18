from django.db import models

from .cif_core import CifAttachment, CifCore, LocationBoxCore, PersonBoxCore, PotentialVictimCore, TransporationCore, VehicleBoxCore

class CifIndia(CifCore):
    # Recruitment
    broker_relation = models.CharField(max_length=126, null=True)
    expected_earning_currency = models.CharField(max_length=126, null=True)
    
    #Legal
    case_exploration_under_16_separated = models.BooleanField( default=False)
    case_exploration_under_14_sent_job = models.BooleanField( default=False)
    case_exploration_under_18_sexually_abused = models.BooleanField( default=False)
    case_exploration_detained_against_will = models.BooleanField( default=False)
    case_exploration_abused = models.BooleanField( default=False)

class PotentialVictimIndia(PotentialVictimCore):
    cif = models.ForeignKey(CifIndia)
    
    def set_parent(self, the_parent):
        self.cif = the_parent

class TransporationIndia(TransporationCore):
    cif = models.ForeignKey(CifIndia)
    
    def set_parent(self, the_parent):
        self.cif = the_parent

class PersonBoxIndia(PersonBoxCore):
    cif = models.ForeignKey(CifIndia)
    
    def set_parent(self, the_parent):
        self.cif = the_parent

class LocationBoxIndia(LocationBoxCore):
    cif = models.ForeignKey(CifIndia)
    
    def set_parent(self, the_parent):
        self.cif = the_parent

class VehicleBoxIndia(VehicleBoxCore):
    cif = models.ForeignKey(CifIndia)
    
    def set_parent(self, the_parent):
        self.cif = the_parent

class CifAttachmentIndia(CifAttachment):
    cif = models.ForeignKey(CifIndia)
    
    def set_parent(self, the_parent):
        self.cif = the_parent
    


