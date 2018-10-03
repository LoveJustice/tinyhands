from django.db import models

LEVEL_CHOICES = [
    ('Country', 'Country'),
    ('State', 'State'),
    ('District', 'District'),
    ('City', 'City'),
    ('VDC', 'VDC'),
    ('Block', 'Block'),
    ('Building', 'Building'),
    ('Village', 'Village'),
    ('Post Office', 'Post Office'),
    ('Upozilla', 'Upozilla'),
]

class Address1(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)

    level = models.CharField(max_length=255, choices=LEVEL_CHOICES, default="District")
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Address2(models.Model):
    name = models.CharField(max_length=255, default="Unknown")
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)
    level = models.CharField(max_length=255, choices=LEVEL_CHOICES, default="VDC")
    address1 = models.ForeignKey(Address1, null=False, on_delete=models.CASCADE)
    canonical_name = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def get_canonical_name(self):
        if self.canonical_name:
            return self.canonical_name.name
        return self.name

    @property
    def get_latitude(self):
        if self.canonical_name:
            return self.canonical_name.latitude
        return self.latitude

    @property
    def get_longitude(self):
        if self.canonical_name:
            return self.canonical_name.longitude
        return self.longitude

    @property
    def get_address1(self):
        if self.canonical_name:
            return self.canonical_name.address1
        return self.address1

    @property
    def is_verified(self):
        return self.verified

    @property
    def is_canonical(self):
        return self.canonical_name is None
