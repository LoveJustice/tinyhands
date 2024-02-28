from django.db import models

from .victim_interview import VictimInterview
from .person import Person


class VictimInterviewPersonBox(models.Model):
    GENDER_CHOICES = [
        ('Male', 'male'),
        ('Female', 'female'),
    ]

    victim_interview = models.ForeignKey(VictimInterview, related_name='person_boxes', on_delete=models.CASCADE)

    who_is_this_relationship_boss_of = models.BooleanField('Boss of...', default=False)
    who_is_this_relationship_coworker_of = models.BooleanField('Co-worker of...', default=False)
    who_is_this_relationship_own_relative_of = models.BooleanField('Own relative of...', default=False)

    who_is_this_role_broker = models.BooleanField('Broker', default=False)
    who_is_this_role_companion = models.BooleanField('Companion', default=False)
    who_is_this_role_india_trafficker = models.BooleanField('India Trafficker', default=False)
    who_is_this_role_contact_of_husband = models.BooleanField('Contact of Husband', default=False)
    who_is_this_role_known_trafficker = models.BooleanField('Known Trafficker', default=False)
    who_is_this_role_manpower = models.BooleanField('Manpower', default=False)
    who_is_this_role_passport = models.BooleanField('Passport', default=False)
    who_is_this_role_sex_industry = models.BooleanField('Sex Industry', default=False)

    person = models.ForeignKey(Person, null=True, blank=True, on_delete=models.CASCADE)

    address_ward = models.CharField('Ward #', max_length=255, blank=True)

    #Think about possibly adding height to the Person model
    height = models.PositiveIntegerField('Height(ft)', null=True, blank=True)
    weight = models.PositiveIntegerField('Weight(kg)', null=True, blank=True)

    physical_description_kirat = models.BooleanField('Kirat', default=False)
    physical_description_sherpa = models.BooleanField('Sherpa', default=False)
    physical_description_madeshi = models.BooleanField('Madeshi', default=False)
    physical_description_pahadi = models.BooleanField('Pahadi', default=False)
    physical_description_newari = models.BooleanField('Newari', default=False)

    appearance_other = models.CharField(max_length=255, blank=True)

    occupation_none = models.BooleanField('None', default=False)
    occupation_agent = models.BooleanField('Agent (taking girls to India)', default=False)
    occupation_business_owner = models.BooleanField('Business owner', default=False)
    occupation_other = models.BooleanField('Other', default=False)
    occupation_wage_labor = models.BooleanField('Wage labor', default=False)
    occupation_job_in_india = models.BooleanField('Job in India', default=False)
    occupation_job_in_gulf = models.BooleanField('Job in Gulf', default=False)
    occupation_farmer = models.BooleanField('Farmer', default=False)
    occupation_teacher = models.BooleanField('Teacher', default=False)
    occupation_police = models.BooleanField('Police', default=False)
    occupation_army = models.BooleanField('Army', default=False)
    occupation_guard = models.BooleanField('Guard', default=False)
    occupation_cook = models.BooleanField('Cook', default=False)
    occupation_driver = models.BooleanField('Driver', default=False)
    occupation_other_value = models.CharField(max_length=255, blank=True)

    political_party_congress = models.BooleanField('Congress', default=False)
    political_party_maoist = models.BooleanField('Maoist', default=False)
    political_party_uml = models.BooleanField('UML', default=False)
    political_party_forum = models.BooleanField('Forum', default=False)
    political_party_tarai_madesh = models.BooleanField('Tarai Madesh', default=False)
    political_party_shadbawona = models.BooleanField('Shadbawona', default=False)
    political_party_rnt = models.BooleanField('Raprapha Nepal Thruhat', default=False)
    political_party_njf = models.BooleanField('Nepal Janadikarik Forum', default=False)
    political_party_loktantrak = models.BooleanField('Loktantrak Party', default=False)
    political_party_dont_know = models.BooleanField('Don\'t Know', default=False)
    political_party_other = models.BooleanField('Other', default=False)
    political_party_other_value = models.CharField(max_length=255, blank=True)

    where_spends_time = models.TextField('Where does he spend most of his time? How can we get ahlod of or find him?', blank=True)

    # Which do you believe about him?

    interviewer_believes_definitely_trafficked = models.BooleanField('Interviewer believes they have definitely trafficked many girls', default=False).set_weight(2)
    interviewer_believes_have_trafficked = models.BooleanField('Interviewer believes they have trafficked some girls', default=False).set_weight(2)
    interviewer_believes_suspects_trafficked = models.BooleanField('Interviewer suspects they are a trafficker', default=False).set_weight(2)
    interviewer_believes_not_trafficker = models.BooleanField('Interviewer doesn\'t believe they are a trafficker', default=False)

    victim_believes_definitely_trafficked = models.BooleanField('Victim believes they have definitely trafficked many girls', default=False).set_weight(2)
    victim_believes_have_trafficked = models.BooleanField('Victim believes they have trafficked some girls', default=False).set_weight(2)
    victim_believes_suspects_trafficked = models.BooleanField('Victim suspects they are a trafficker', default=False).set_weight(2)
    victim_believes_not_trafficker = models.BooleanField('Victim doesn\'t believe they are a trafficker', default=False)

    associated_with_place = models.BooleanField(null=True)
    associated_with_place_value = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "VIF {}".format(self.victim_interview.vif_number)
