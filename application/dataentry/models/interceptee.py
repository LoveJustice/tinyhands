from django.db import models

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from .person import Person
from .interception_record import InterceptionRecord


class Interceptee(models.Model):
    KIND_CHOICES = [
        ('v', 'Victim'),
        ('t', 'Trafficker'),
    ]
    photo = models.ImageField(upload_to='interceptee_photos', default='', blank=True)
    photo_thumbnail = ImageSpecField(source='photo',
                                     processors=[ResizeToFill(200, 200)],
                                     format='JPEG',
                                     options={'quality': 80})
    interception_record = models.ForeignKey(InterceptionRecord, related_name='interceptees', on_delete=models.CASCADE)
    kind = models.CharField(max_length=4, choices=KIND_CHOICES)
    relation_to = models.CharField(max_length=255, blank=True)
    person = models.ForeignKey(Person, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return "{} ({})".format(self.person.full_name, self.id)

    def address1_as_string(self):
        rtn = ''
        try:
            rtn = self.person.address1
        finally:
            return rtn

    def address2_as_string(self):
        rtn = ''
        try:
            rtn = self.person.address2
        finally:
            return rtn
