from django.db import models
from .irf_core import IrfAttachment, IrfCore, IntercepteeCore

class IrfMalawi(IrfCore):
    # Group - Malawi specific
    who_in_group_alone = models.BooleanField('Alone', default=False)
    who_in_group_relative = models.BooleanField('Own brother, sister / relative', default=False)
    meeting_someone_across_border = models.BooleanField('Is meeting a someone just across border', default=False)
    traveling_with_someone_not_with_them = models.BooleanField('Was travelling with someone not with them', default=False)
    group_facebook = models.BooleanField('Facebook', default=False)
    group_other_website = models.CharField(max_length=127, blank=True)
    relationship_social_media = models.BooleanField('Met on social media', default=False)
    relationship_to_get_married = models.BooleanField('Coming to get married', default=False)
    with_non_relative = models.BooleanField('With non-relatives', default=False)
    met_within_past_2_months = models.BooleanField('Met within the past 2 months', default=False)
    dont_know_or_conflicting_answers = models.BooleanField('They don’t know or provide conflicting answers', default=False)
    undocumented_children_in_group = models.BooleanField('Undocumented child(ren) in the group', default=False)
    met_on_the_way = models.BooleanField('Met on their way', default=False)
    group_young_women_kids = models.BooleanField('Group of young women / kids', default=False)
    who_in_group_engaged = models.BooleanField('Engaged', default=False)
    who_in_group_dating = models.BooleanField('Dating couple', default=False)
    who_in_group_pv_under_14 = models.BooleanField('PV is under 14', default=False)
    relationship_arranged_by_other = models.BooleanField('Non-relative(s) organized their travel', default=False)
    host_non_relative_paid = models.BooleanField('Non-relative(s) paid their travel expenses', default=False)
    mobile_phone_taken_away = models.BooleanField('Their mobile phone was taken away', default=False)
    contradiction_between_stories = models.BooleanField('Contradiction between stories', default=False)
    wife_under_18 = models.BooleanField('Wife/fiancee is under 18', default=False)
    
    # Destination - Malawi specific
    employment_massage_parlor = models.BooleanField('Massage parlor', default=False)
    young_woman_going_to_mining_town = models.BooleanField('Young woman going for a job in a mining town', default=False)
    person_speaking_on_their_behalf = models.BooleanField('Person is not speaking on their own behalf / someone is speaking for them', default=False)
    seasonal_farm_work = models.BooleanField('Going for seasonal farm work', default=False)
    unregistered_mine = models.BooleanField('Going to work at unregistered mine', default=False)
    no_company_website = models.BooleanField('Could not find company website', default=False)
    distant_relative_paying_for_education = models.BooleanField('Distant relative is paying for education', default=False)
    no_school_website = models.BooleanField('No school website', default=False)
    job_confirmed = models.BooleanField('Job confirmed', default=False)
    valid_id_or_enrollment_documents = models.BooleanField('Valid ID card or enrollment documents', default=False)
    doesnt_speak_destination_language = models.BooleanField("Doesn't speak language of destination", default=False)
    where_going_doesnt_know = models.BooleanField("Don't know where they are going", default=False)
    job_confirmed = models.BooleanField('Job confirmed', default=False)
    valid_id_or_enrollment_documents = models.BooleanField('Valid ID card or enrollment documents', default=False)
    enrollment_confirmed = models.BooleanField('Enrollment confirmed', default=False)
    purpose_for_going_other = models.CharField(max_length=127, blank=True)
    
    # Family - Malawi specific
    
    # Signs - Malawi specific
    which_contact = models.CharField(max_length=127, blank=True)
    name_of_contact = models.CharField(max_length=127, default='', blank=True)
    initial_signs = models.CharField(max_length=127, default='', blank=True)
    
    # Final Procedures - Malawi specific
    case_notes = models.TextField('Case Notes', blank=True)
    handed_over_to =  models.CharField(max_length=127, default='', blank=True)
    
class IntercepteeMalawi(IntercepteeCore):
    interception_record = models.ForeignKey(IrfMalawi, related_name='interceptees', on_delete=models.CASCADE)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return "{} ({})".format(self.person.full_name, self.id)
    
    def set_parent(self, the_parent):
        self.interception_record = the_parent

class IrfAttachmentMalawi(IrfAttachment):
    interception_record = models.ForeignKey(IrfMalawi)
    
    def set_parent(self, the_parent):
        self.interception_record = the_parent