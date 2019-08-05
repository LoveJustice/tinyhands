from django.db import models
from .irf_core import IrfAttachment, IrfCore, IntercepteeCore

class IrfGhana(IrfCore):
    # Group - Ghana specific
    group_facebook = models.BooleanField('Facebook', default=False)
    group_other_website = models.CharField(max_length=127, blank=True)
    who_in_group_adults = models.BooleanField('Adult(s)', default=False)
    who_in_group_children_with_parents = models.BooleanField('Child(ren) with parents', default=False)
    who_in_group_children_with_other_adults = models.BooleanField('Child(ren) with other adults', default=False)
    who_in_group_children_non_relative = models.BooleanField('Non-relative', default=False)
    who_in_group_children_relative = models.CharField(max_length=127, blank=True)
    who_in_group_children_alone = models.BooleanField('Child(ren) traveling alone', default=False)
    group_adult_meeting_someone_at_destination = models.BooleanField("(Adult) meeting someone at destination who they don't know at all or don't know well", default=False)
    group_met_companion_on_way = models.BooleanField('Met companion on their way', default=False)
    mobile_phone_taken_away = models.BooleanField('Their mobile phone was taken away', default=False)
    relationship_to_get_married = models.BooleanField('Going to get married', default=False)
    group_opportunity_for_child_too_good = models.BooleanField("Someone approached them with an opportunity for their child that's too good to be true", default=False)
    group_alleged_parents_conflicting_answers = models.BooleanField("Alleged parent(s) don't know or provide conflicting answers to basic questions", default=False)
    group_relation_verified = models.BooleanField('Relationship and Intention Verified', default=False)
    undocumented_children_in_group = models.BooleanField('Undocumented child(ren) in the group', default=False)
    where_going_arranged_by_other = models.BooleanField('Non-relatives organized their travel', default=False)
    where_going_someone_paid_expenses = models.BooleanField('Non relatives paid for their travel', default=False)
    group_child_fearful = models.BooleanField('Child(ren) seem uncomfortable/fearful', default=False)
    group_child_meeting_someone_at_destination = models.BooleanField("(Child) meeting someone at destination who they don't know at all or don't know well", default=False)
    traveling_with_someone_not_with_them = models.BooleanField('Was travelling with someone not with them', default=False)
    contradiction_between_stories = models.BooleanField('Contradiction between stories', default=False)
    
    # Destination - Ghana specific
    destination_lake_volta_region = models.BooleanField('Going to Lake Volta Region', default=False)
    doesnt_speak_destination_language = models.BooleanField("Doesn't speak language of destination", default=False)
    where_going_doesnt_know = models.BooleanField("Doesn't know where they are going", default=False)
    person_speaking_on_their_behalf = models.BooleanField('Person is not speaking on their own behalf / someone is speaking for them', default=False)
    destination_other = models.CharField(max_length=127, blank=True)
    employment_massage_parlor = models.BooleanField('Massage parlor', default=False)
    no_company_website = models.BooleanField('Could not find company website', default=False)
    distant_relative_paying_for_education = models.BooleanField('Distant relative is paying for education', default=False)
    no_school_website = models.BooleanField('No school website', default=False)
    purpose_for_going_other = models.CharField(max_length=127, blank=True)
    job_confirmed = models.BooleanField('Job confirmed', default=False)
    valid_id_or_enrollment_documents = models.BooleanField('Valid ID card or enrollment documents', default=False)
    enrollment_confirmed = models.BooleanField('Enrollment confirmed', default=False)
    
    # Family - Ghana specific
    case_notes = models.TextField('Case Notes', blank=True)
    
    # Signs - Ghana specific
    which_contact = models.CharField(max_length=127, blank=True)
    name_of_contact = models.CharField(max_length=127, default='', blank=True)
    initial_signs = models.CharField(max_length=127, default='', blank=True)
    
    
class IntercepteeGhana(IntercepteeCore):
    interception_record = models.ForeignKey(IrfGhana, related_name='interceptees', on_delete=models.CASCADE)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return "{} ({})".format(self.person.full_name, self.id)
    
    def set_parent(self, the_parent):
        self.interception_record = the_parent

class IrfAttachmentGhana(IrfAttachment):
    interception_record = models.ForeignKey(IrfGhana)
    
    def set_parent(self, the_parent):
        self.interception_record = the_parent