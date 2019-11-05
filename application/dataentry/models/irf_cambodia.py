from django.db import models
from .irf_core import IrfAttachment, IrfCore, IntercepteeCore
from .person import Person

class IrfCambodia(IrfCore):
    who_in_group_alone = models.BooleanField('Alone', default=False)
    who_in_group_relative = models.BooleanField('Own brother, sister / relative', default=False)
    who_in_group_broker = models.BooleanField('Broker/Other Person', default=False)
    meeting_someone_across_border = models.BooleanField('Is meeting a someone just across border', default=False)
    meeting_someone_they_dont_know = models.BooleanField("Supposed to meet someone they don't know", default=False)
    crossing_border_separately = models.BooleanField('Someone who is crossing border separately', default=False)
    agent_sent_them_on = models.BooleanField('An agent who sent them on', default=False)
    relationship_married_two_months = models.BooleanField('During the past 2 months', default=False)
    different_ethnicities = models.BooleanField('Appear to be of different ethnicities', default=False)


    thailand_destination = models.CharField(max_length=127, blank=True)
    malaysia_destination = models.CharField(max_length=127, blank=True)
    where_going_other = models.CharField(max_length=127, blank=True)
    where_going_doesnt_know = models.BooleanField("Don't know where going", default=False)
    work_sector_agriculture = models.BooleanField('Agriculture', default=False)
    work_sector_construction = models.BooleanField('Construction', default=False)
    work_sector_domestic_service = models.BooleanField('Domestic Services', default=False)
    work_sector_dont_know = models.BooleanField("Don't know", default=False)
    work_sector_factory = models.BooleanField('Factory', default=False)
    work_sector_fishing = models.BooleanField('Fishing', default=False)
    work_sector_hospitality = models.BooleanField('Hospitality', default=False)
    work_sector_logging = models.BooleanField('Logging', default=False)
    work_sector_other = models.CharField(max_length=127, blank=True)
    expected_earning = models.CharField(max_length=127, blank=True)
    no_company_phone = models.BooleanField('No company phone number', default=False)
    job_confirmed = models.BooleanField('job confirmed', default=False)
    valid_id_or_enrollment_documents = models.BooleanField('Valid ID card or enrollment documents', default=False)
    enrollment_confirmed = models.BooleanField('Enrollment confirmed', default=False)
    purpose_for_going_other = models.CharField(max_length=127, blank=True)
    took_out_loan = models.CharField(max_length=127, blank=True)
    recruited_broker = models.BooleanField('Broker/Agent', default=False)
    how_recruited_broker_approached = models.BooleanField('Broker approached them', default=False)
    met_broker_through_advertisement = models.BooleanField('Through advertisment', default=False)
    met_broker_online = models.CharField(max_length=127, blank=True)
    how_recruited_broker_other = models.CharField(max_length=127, blank=True)
    broker = models.ForeignKey(Person, null=True, blank=True)
    broker_company = models.CharField(max_length=127, blank=True)
    unwilling_to_give_info_about_broker = models.BooleanField('unwilling to give information about them', default=False)

    initial_signs = models.TextField('Initial Signs', blank=True)
    
    case_notes = models.TextField('Case Notes', blank=True)
    
class IntercepteeCambodia(IntercepteeCore):
    interception_record = models.ForeignKey(IrfCambodia, related_name='interceptees', on_delete=models.CASCADE)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return "{} ({})".format(self.person.full_name, self.id)
    
    def set_parent(self, the_parent):
        self.interception_record = the_parent

class IrfAttachmentCambodia(IrfAttachment):
    interception_record = models.ForeignKey(IrfCambodia)
    
    def set_parent(self, the_parent):
        self.interception_record = the_parent