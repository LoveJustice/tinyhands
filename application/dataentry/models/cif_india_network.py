from django.db import models

from .cif_core import CifAttachment, CifCore, LocationBoxCore, PersonBoxCore, PotentialVictimCore, TransporationCore, VehicleBoxCore

class CifIndiaNetwork(CifCore):
    # Recruitment
    broker_relation = models.CharField(max_length=126, null=True)
    expected_earning_currency = models.CharField(max_length=126, null=True)
    
    #Legal
    case_exploration_under_16_separated = models.BooleanField( default=False)
    case_exploration_under_14_sent_job = models.BooleanField( default=False)
    case_exploration_under_18_sexually_abused = models.BooleanField( default=False)
    case_exploration_detained_against_will = models.BooleanField( default=False)
    case_exploration_abused = models.BooleanField( default=False)

class PotentialVictimIndiaNetwork(PotentialVictimCore):
    cif = models.ForeignKey(CifIndiaNetwork)
    
    def set_parent(self, the_parent):
        self.cif = the_parent

class TransporationIndiaNetwork(TransporationCore):
    cif = models.ForeignKey(CifIndiaNetwork)
    
    def set_parent(self, the_parent):
        self.cif = the_parent

class PersonBoxIndiaNetwork(PersonBoxCore):
    cif = models.ForeignKey(CifIndiaNetwork)
    
    def set_parent(self, the_parent):
        self.cif = the_parent

class LocationBoxIndiaNetwork(LocationBoxCore):
    cif = models.ForeignKey(CifIndiaNetwork)
    
    def set_parent(self, the_parent):
        self.cif = the_parent

class VehicleBoxIndiaNetwork(VehicleBoxCore):
    cif = models.ForeignKey(CifIndiaNetwork)
    
    def set_parent(self, the_parent):
        self.cif = the_parent

class CifAttachmentIndiaNetwork(CifAttachment):
    cif = models.ForeignKey(CifIndiaNetwork)
    
    def set_parent(self, the_parent):
        self.cif = the_parent
    


