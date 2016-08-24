from django.db import models


class FuzzyMatching(models.Model):
    address1_cutoff = models.PositiveIntegerField(default=70)
    address1_limit = models.PositiveIntegerField(default=5)
    address2_cutoff = models.PositiveIntegerField(default=70)
    address2_limit = models.PositiveIntegerField(default=5)
    person_cutoff = models.PositiveIntegerField(default=90)
    person_limit = models.PositiveIntegerField(default=10)
    # PHONE NUMBER MATCHING FOR FUTURE USE
    # phone_number_cutoff = models.PositiveIntegerField(default=0)
    # phone_number_limit = models.PositiveIntegerField(default=0)
