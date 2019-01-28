from django.db import models
from .irf_core import IrfCore, IntercepteeCore

class IrfBenin(IrfCore):
    # Group - Benin specific
    who_in_group_alone = models.BooleanField('Alone', default=False)
    who_in_group_relative = models.BooleanField('Own brother, sister / relative', default=False)
    meeting_someone_across_border = models.BooleanField('Is meeting a someone just across border', default=False)
    traveling_with_someone_not_with_them = models.BooleanField('Was travelling with someone not with them', default=False)
    group_facebook = models.BooleanField('Facebook', default=False)
    group_other_website = models.CharField(max_length=127, blank=True)
    relationship_social_media = models.BooleanField('Met on social media', default=False)
    relationship_to_get_married = models.BooleanField('Coming to get married', default=False)
    appears_under_spell = models.BooleanField('Appears to be under a spell/witchcraft', default=False)
    group_young_women_kids = models.BooleanField('Group of young women or kids', default=False)
    with_non_relative = models.BooleanField('With non-relatives', default=False)
    met_within_past_2_months = models.BooleanField('Met within the past 2 months', default=False)
    dont_know_or_conflicting_answers = models.BooleanField('They don’t know or provide conflicting answers', default=False)
    undocumented_children_in_group = models.BooleanField('Undocumented child(ren) in the group', default=False)
    relationship_arranged_by_other = models.BooleanField('Non-relatives organized their travel', default=False)
    where_going_someone_paid_expenses = models.BooleanField('Non relatives paid for their travel', default=False)
    met_on_the_way = models.BooleanField('Met on their way', default=False)
    non_relative_met_within_past_2_months = models.BooleanField('Met within the past 2 months', default=False)
    mobile_phone_taken_away = models.BooleanField('Their mobile phone was taken away', default=False)
    
    # Destination - Benin specific
    doesnt_speak_local_language = models.BooleanField("Doesn't speak English", default=False)
    doesnt_speak_destination_language = models.BooleanField("Doesn't speak language of destination", default=False)
    where_going_middle_east = models.BooleanField("Going to a country in the Middle East / Persian Gulf", default=False)
    where_going_doesnt_know = models.BooleanField("Doesn't know where they are going", default=False)
    person_speaking_on_their_behalf = models.BooleanField('Person is not speaking on their own behalf / someone is speaking for them', default=False)
    going_abroad_domestic_work = models.BooleanField('Going abroad for domestic work', default=False)
    job_just_graduated = models.BooleanField('Just graduated', default=False)
    visa_for_domestic_work = models.BooleanField('Have visa for domestic work in passport', default=False)
    employment_massage_parlor = models.BooleanField('Massage parlor', default=False)
    no_company_website = models.BooleanField('Could not find company website', default=False)
    distant_relative_paying_for_education = models.BooleanField('Distant relative is paying for education', default=False)
    no_school_website = models.BooleanField('No school website', default=False)
    
    # Family - Benin specific
    
    # Signs - Benin specific
    which_contact = models.CharField(max_length=127, blank=True)
    name_of_contact = models.CharField(max_length=127, default='', blank=True)
    initial_signs = models.CharField(max_length=127, default='', blank=True)
    
    # Final Procedures - Benin specific
    case_notes = models.TextField('Case Notes', blank=True)
    scanned_form = models.FileField('Attach scanned copy of form (pdf or image)', upload_to='scanned_irf_forms', default='', blank=True)
    interception_made = models.CharField(max_length=127, null=True)
    handed_over_to =  models.CharField(max_length=127, default='', blank=True)
    
class IntercepteeBenin(IntercepteeCore):
    interception_record = models.ForeignKey(IrfBenin, related_name='interceptees', on_delete=models.CASCADE)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return "{} ({})".format(self.person.full_name, self.id)
    
    def set_parent(self, the_parent):
        self.interception_record = the_parent