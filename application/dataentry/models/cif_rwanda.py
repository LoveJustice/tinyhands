from django.db import models

from .cif_core import CifAttachment, CifCore, LocationBoxCore, PersonBoxCore, PotentialVictimCore, TransporationCore, VehicleBoxCore

class CifRwanda(CifCore):
    # Recruitment
    how_recruited_promised_education = models.BooleanField(default=False)
    how_recruited_broker_asked_pb_work_visa = models.BooleanField(default=False)
    how_recruited_broker_asked_pb_work_visa_pb = models.CharField(max_length=126, null=True)
    
    # Travel
    border_cross_official = models.BooleanField(default=False)
    border_cross_illegal = models.BooleanField(default=False)
    pv_has_no_id = models.BooleanField(default=False)
    
    #Legal
    legal_action_taken_staff_dont_believe_trafficking = models.BooleanField(default=False)
    legal_action_taken_staff_couldnt_reestablish_contact = models.BooleanField(default=False)
    

class PotentialVictimRwanda(PotentialVictimCore):
    cif = models.ForeignKey(CifRwanda)
    
    def set_parent(self, the_parent):
        self.cif = the_parent

class TransporationRwanda(TransporationCore):
    cif = models.ForeignKey(CifRwanda)
    
    def set_parent(self, the_parent):
        self.cif = the_parent

class PersonBoxRwanda(PersonBoxCore):
    cif = models.ForeignKey(CifRwanda)
    how_well_does_pv_know = models.CharField(max_length=126, null=True)
    
    def set_parent(self, the_parent):
        self.cif = the_parent

class LocationBoxRwanda(LocationBoxCore):
    cif = models.ForeignKey(CifRwanda)
    
    def set_parent(self, the_parent):
        self.cif = the_parent

class VehicleBoxRwanda(VehicleBoxCore):
    cif = models.ForeignKey(CifRwanda)
    
    def set_parent(self, the_parent):
        self.cif = the_parent

class CifAttachmentRwanda(CifAttachment):
    cif = models.ForeignKey(CifRwanda)
    
    def set_parent(self, the_parent):
        self.cif = the_parent
    


