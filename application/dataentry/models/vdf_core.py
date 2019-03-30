from django.db import models

from .person import Person
from .form import BaseCard, BaseForm

# Class to store an instance of the VDF data.
# This should contain data that is common for all VDFs and is not expected to be changed
class VdfCore(BaseForm):
    # Top Box
    vdf_number = models.CharField('IRF #:', max_length=20, unique=True)
    staff_name = models.CharField('Staff Name:', max_length=255)
    discharge_date = models.DateField('Incident date', null=True)
    location = models.CharField('Location:', max_length=255)
    
    # Victim/Family Info
    victim = models.ForeignKey(Person, null=True, blank=True)
    occupation = models.CharField('Occupation', max_length=126, null=True)
    guardian_name = models.CharField('Guardian Name', max_length=126, null=True)
    guardian_phone = models.CharField('Guardian Phone', max_length=126, null=True)
    
    # Home Situation Assessment
    guardian_know_destination = models.CharField('Did your guardian know you were traveling to intended destination?', max_length=126, null=True)
    family_guardian_pressure = models.CharField("Did your family/guardian pressure you in any way to accept the broker's offer?", max_length=126, null=True)
    try_to_send_overseas_again = models.CharField('If they attempted, do you think they will try to send you overseas again?', max_length=126, null=True)
    feel_safe_with_guardian = models.CharField('Do you feel safe at home with your guardian?', max_length=126, null=True)
    do_you_want_to_go_home = models.CharField('Do you want to go home?', max_length=126, null=True)
    sexual_abuse = models.CharField('Sexual Abuse', max_length=126, null=True)
    physical_abuse = models.CharField('Physical Abuse', max_length=126, null=True)
    emotional_abuse = models.CharField('Emotional Abuse', max_length=126, null=True)
    guardian_drink_alcohol = models.CharField('Does the Guardian drink alcohol?', max_length=126, null=True)
    guardian_use_drugs = models.CharField('Does the Guardian use drugs?', max_length=126, null=True)
    family_economic_situation = models.CharField('Economic Situation of Family', max_length=126, null=True)
    express_suicidal_thoughts = models.CharField('Did the victim express any suicidal thoughts at any point?', max_length=126, null=True)
    total_situational_alarms = models.PositiveIntegerField('Total Situational Alarms', null=True, blank=True)
    station_recommendation_for_victim = models.CharField('What is the Border Station recommendation about where the victim should go?', max_length=126, null=True)

    # Awareness/Assessment
    staff_share_gospel = models.CharField('Did the staff share the gospel with the victim?', max_length=126, null=True)
    share_gospel_film = models.BooleanField('Film', default=False)
    share_gospel_tract = models.BooleanField('Tract', default=False)
    share_gospel_oral = models.BooleanField('Oral Preaching', default=False)
    share_gospel_testimony = models.BooleanField('Shared Personal Testimony', default=False)
    share_gospel_book = models.BooleanField('Message Book', default=False)
    share_gospel_other = models.CharField('Other', max_length=126, null=True)
    awareness_of_exploitation_before_interception = models.CharField('Before you were intercepted, were you aware that migrants going abroad are often deceived and end up in very exploitative situations?', max_length=126, null=True)
    victim_heard_message_before = models.CharField('Had you ever heard the message before?', max_length=126, null=True)
    what_victim_believes_now = models.CharField('What do you believe now?', max_length=126, null=True)
    transit_staff_polite = models.PositiveIntegerField('Transit Staff Polite and Respectful', null=True, blank=True)
    trafficking_awareness = models.PositiveIntegerField('Trafficking Awareness', null=True, blank=True)
    shelter_staff_polite = models.PositiveIntegerField('Shelter Staff Polite and Respectful', null=True, blank=True)
    shelter_accomodation = models.PositiveIntegerField('Shelter Accomodations', null=True, blank=True)
    
    # Release Information
    victim_still_at_shelter = models.CharField('Is victim still in the care of Border Station?', max_length=126, null=True)
    date_victim_left = models.DateField('What date did victim leave the care of the Station', null=True)
    someone_pick_up_victim = models.CharField('Did someone pick up victim from the station?', max_length=126, null=True)
    who_victim_released = models.CharField('If yes, who was the victim released to?', max_length=126, null=True)
    who_victim_released_name = models.CharField('Name of person whom the victim was released to', max_length=126, null=True)
    who_victim_released_phone = models.CharField('Phone Number', max_length=126, null=True)
    where_victim_sent = models.CharField('Where was the victim sent', max_length=126, null=True)

    # Final Procedures
    consent_to_use_information = models.CharField('I give consent to use any information I have shared throughout the duration of my time with the staff for operational and awareness purposes', max_length=126, null=True)
    victim_signature = models.BooleanField('Victim Signature', default=False)
    guardian_signature = models.BooleanField('Guardian Signature', default=False)
    case_notes = models.TextField('Case Notes', blank=True)



    class Meta:
        abstract = True

class VdfAttachment(BaseCard):
    attachment_number = models.PositiveIntegerField(null=True, blank=True)
    description = models.CharField(max_length=126, null=True)
    attachment = models.FileField('Attach scanned copy of form (pdf or image)', upload_to='vdf_attachments')
    
    class Meta:
        abstract = True
    
