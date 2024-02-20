from django.db import models
from django.db.models import JSONField

from .person import Person
from .master_person import MasterPerson, MatchType
from accounts.models import Account

class MatchAction(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)

class MatchHistory(models.Model):
    master1 = models.ForeignKey(MasterPerson, related_name='masterHistory1', on_delete=models.CASCADE)
    master2 = models.ForeignKey(MasterPerson, related_name='masterHistory2', null=True, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, null=True, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    match_type = models.ForeignKey(MatchType, null=True, on_delete=models.CASCADE)
    action = models.ForeignKey(MatchAction, on_delete=models.CASCADE)    # create MP, create match , remove, merge, type change
    timestamp = models.DateTimeField(auto_now_add=True)
    matched_by = models.ForeignKey(Account, null=True, on_delete=models.SET_NULL)
    match_results = JSONField(null=True)