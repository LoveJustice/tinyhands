from django.db import models
from django.contrib.postgres.fields import JSONField
from .form import BaseCard
from .form import BaseForm
from .incident import Incident

class LocationForm(BaseForm):
    # Top
    lf_number = models.CharField(max_length=20, unique=True)
    
    # Other incidents that might be associated with this suspect
    associated_incidents = models.ManyToManyField(Incident, related_name='location_associated_incidents')
    
    # Incidents with which this suspect is known to be involved
    # Initially only one Incident
    incidents = models.ManyToManyField(Incident)
    
    evidence = models.TextField(blank=True)
    
class LocationInformation(BaseCard):
    lf = models.ForeignKey(LocationForm, on_delete=models.CASCADE)
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, null=True)
    source_type = models.CharField(max_length=126, null=True)
    source_title = models.CharField(max_length=126, blank=True)
    interviewer_name = models.CharField(max_length=126, blank=True)
    interview_date = models.DateField(null=True, default=None)
    location = models.CharField(max_length=255, blank=True)
    place = models.CharField(max_length=126, null=True)
    place_detail = models.CharField(max_length=126, null=True)
    place_kind = models.CharField(max_length=126, null=True)
    address = JSONField(null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    phone = models.CharField(max_length=126, null=True)
    name_signboard = models.CharField(max_length=126, null=True)
    location_in_town = models.CharField(max_length=126, null=True)
    color = models.CharField(max_length=126, null=True)
    number_of_levels = models.CharField(max_length=126, null=True)
    description = models.TextField('Descriptive Features', blank=True) # address notes
    nearby_landmarks = models.CharField(max_length=126, null=True)
    
    def set_parent(self, the_parent):
        self.lf = the_parent

class LocationAssociation(BaseCard):
    lf = models.ForeignKey(LocationForm, on_delete=models.CASCADE)
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, null=True)
    source_type = models.CharField(max_length=126, null=True)
    source_title = models.CharField(max_length=126, blank=True)
    interviewer_name = models.CharField(max_length=126, blank=True)
    interview_date = models.DateField(null=True, default=None)
    location = models.CharField(max_length=255, blank=True)
    persons_in_charge = models.CharField(max_length=126, null=True)
    pvs_visited = models.CharField(max_length=126, null=True)
    stay_how_long = models.CharField(max_length=126, null=True)
    start_date = models.DateField(null=True, default=None)
    attempt_hide = models.CharField(max_length=126, null=True)
    attempt_explanation = models.CharField(max_length=126, null=True)
    free_to_go = models.CharField(max_length=126, null=True)
    free_to_go_explanation = models.CharField(max_length=126, null=True)
    suspects_associative = models.CharField(max_length=126, null=True)
    
    def set_parent(self, the_parent):
        self.suspect = the_parent
    
class LocationEvaluation(BaseCard):
    lf = models.ForeignKey(LocationForm, on_delete=models.CASCADE)
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE)
    evaluator_type = models.CharField(max_length=126, null=True)
    evaluator_name = models.CharField(max_length=126, null=True)
    evaluation = models.CharField(max_length=126, null=True)
    
    def set_parent(self, the_parent):
        self.suspect = the_parent

class LocationAttachment(BaseCard):
    lf = models.ForeignKey(LocationForm, on_delete=models.CASCADE)
    attachment_number = models.PositiveIntegerField(null=True, blank=True)
    description = models.CharField(max_length=126, null=True)
    attachment = models.FileField('Attach scanned copy of form (pdf or image)', upload_to='suspect_attachments')
    private_card = models.BooleanField(default=True)
    option = models.CharField(max_length=126, null=True)
    
    def set_parent(self, the_parent):
        self.suspect = the_parent
        
    def is_private(self):
        return self.private_card