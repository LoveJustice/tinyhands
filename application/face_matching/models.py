from django.db import models
from django.contrib.postgres.fields import ArrayField
from dataentry.models.person import Person

class FaceEncoding(models.Model):
    person = models.ForeignKey(Person, primary_key=True,
                                  to_field="id", db_column="person_id", on_delete=models.DO_NOTHING)
    face_encoding = ArrayField(models.FloatField(
        blank=True), blank=True, size=128)
    outcome = models.TextField(blank=True)

    class Meta:
        managed = False  # TODO: remove me
        db_table = 'face_encodings'

        def __str__(self):
            return self.person_id


class AnalyzedPerson(models.Model):
    face_photo = models.ImageField(width_field=300, height_field=300)
    # TODO: Use file uploaded to client
    full_photo = models.ImageField(width_field=300, height_field=300)
    face_analysis = models.TextField()


class MatchingPerson(models.Model):
    GENDER_CHOICES = [('M', 'm'), ('F', 'f')]

    full_name = models.CharField(max_length=255, null=True, blank=True)
    person_id = models.CharField(max_length=6)
    gender = models.CharField(max_length=4, choices=GENDER_CHOICES, blank=True)
    role = models.CharField(max_length=126, null=True)
    face_photo = models.ImageField(width_field=300, height_field=300)
    full_photo = models.ImageField(width_field=300, height_field=300)
    irf_number = models.CharField(max_length=6)
    nationality = models.CharField(max_length=127, blank=True, default='')
    age_at_interception = models.PositiveIntegerField(null=True, blank=True)
    date_of_interception = models.DateField('Interception date', null=True, default=None)
    face_analysis = models.TextField()
    face_distance = models.DecimalField(max_digits=2, decimal_places=2)


class MatchingData(models.Model):
    analyzedPerson = models.OneToOneField(AnalyzedPerson, on_delete=models.CASCADE)
    matchingPersons = models.ForeignKey(MatchingPerson, on_delete=models.CASCADE)
