from django.db import models

from .cif_core import CifAttachment, CifCore, LocationBoxCore, PersonBoxCore, PotentialVictimCore, TransporationCore, VehicleBoxCore

class CifOsi(CifCore):
    #Top
    collection_date = models.DateField(null=True)
    source_url = models.CharField(max_length=126, null=True)
    publication = models.CharField(max_length=126, null=True)
    headline = models.CharField(max_length=126, null=True)
    article_date  = models.DateField(null=True)
    
    # Recruitment
    broker_relation = models.CharField(max_length=126, null=True)
    expected_earning_currency = models.CharField(max_length=126, null=True)
    
class PotentialVictimOsi(PotentialVictimCore):
    cif = models.ForeignKey(CifOsi)
    
    def set_parent(self, the_parent):
        self.cif = the_parent

class TransporationOsi(TransporationCore):
    cif = models.ForeignKey(CifOsi)
    
    def set_parent(self, the_parent):
        self.cif = the_parent

class PersonBoxOsi(PersonBoxCore):
    cif = models.ForeignKey(CifOsi)
    
    def set_parent(self, the_parent):
        self.cif = the_parent

class LocationBoxOsi(LocationBoxCore):
    cif = models.ForeignKey(CifOsi)
    
    def set_parent(self, the_parent):
        self.cif = the_parent

class VehicleBoxOsi(VehicleBoxCore):
    cif = models.ForeignKey(CifOsi)
    
    def set_parent(self, the_parent):
        self.cif = the_parent

class CifAttachmentOsi(CifAttachment):
    cif = models.ForeignKey(CifOsi)
    
    def set_parent(self, the_parent):
        self.cif = the_parent
    


