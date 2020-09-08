from django.db import models
from .master_person import PersonMatch
from .country import Country

class PendingMatch(models.Model):
    the_key = models.CharField(max_length=100, primary_key=True)
    person_match = models.ForeignKey(PersonMatch, on_delete=models.DO_NOTHING)
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING)
    
    class Meta:
        managed=False
        unique_together = (('person_match', 'country'),)
        db_table = 'pendingmatch'