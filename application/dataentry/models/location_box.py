from django.db import models
from .addresses import Address1, Address2
from .victim_interview import VictimInterview


class VictimInterviewLocationBox(models.Model):
    victim_interview = models.ForeignKey(VictimInterview, related_name='location_boxes', on_delete=models.CASCADE)

    which_place_india_meetpoint = models.BooleanField('India Meet Point', default=False)
    which_place_manpower = models.BooleanField('Manpower', default=False)
    which_place_transit_hideout = models.BooleanField('Transit Hideout', default=False)
    which_place_destination = models.BooleanField('Destination', default=False)
    which_place_passport = models.BooleanField('Passport', default=False)
    which_place_nepal_meet_point = models.BooleanField('Nepal Meet Point', default=False)
    which_place_known_location = models.BooleanField('Known Location', default=False)
    which_place_sex_industry = models.BooleanField('Sex Industry', default=False)

    what_kind_place_persons_house = models.BooleanField('Person\'s House', default=False)
    what_kind_place_bus_station = models.BooleanField('Bus station', default=False)
    what_kind_place_train_station = models.BooleanField('Train station', default=False)
    what_kind_place_shop = models.BooleanField('Shop', default=False)
    what_kind_place_factory = models.BooleanField('Factory', default=False)
    what_kind_place_brothel = models.BooleanField('Brothel', default=False).set_weight(2)
    what_kind_place_hotel = models.BooleanField('Hotel', default=False)

    signboard = models.CharField(max_length=255, blank=True)
    location_in_town = models.CharField(max_length=255, blank=True)
    address1 = models.ForeignKey(Address1, null=True, on_delete=models.CASCADE)
    address2 = models.ForeignKey(Address2, null=True, on_delete=models.CASCADE)

    phone = models.CharField('Phone #', max_length=255, blank=True)
    color = models.CharField(max_length=255, blank=True)
    number_of_levels = models.CharField('# of Levels', max_length=255, blank=True)
    compound_wall = models.CharField(max_length=255, blank=True)
    gate_color = models.CharField(max_length=255, blank=True)
    roof_type = models.CharField(max_length=255, blank=True)
    roof_color = models.CharField(max_length=255, blank=True)
    person_in_charge = models.CharField(max_length=255, blank=True)
    nearby_landmarks = models.CharField(max_length=255, blank=True)
    nearby_signboards = models.CharField(max_length=255, blank=True)
    other = models.CharField(max_length=255, blank=True)

    interviewer_believes_trafficked_many_girls = models.BooleanField('Interviewer believes this location is definitely used to traffic many victims', default=False).set_weight(2)
    interviewer_believes_trafficked_some_girls = models.BooleanField('Interviewer believes this location has been used repeatedly to traffic some victims', default=False).set_weight(2)
    interviewer_believes_suspect_used_for_trafficking = models.BooleanField('Interviewer suspects this location has been used for trafficking', default=False).set_weight(2)
    interviewer_believes_not_used_for_trafficking = models.BooleanField('Interviewer does not believe this location is used for trafficking', default=False)

    victim_believes_trafficked_many_girls = models.BooleanField('Victim believes this location is definitely used to traffic many victims', default=False).set_weight(2)
    victim_believes_trafficked_some_girls = models.BooleanField('Victim believes this location has been used repeatedly to traffic some victims', default=False).set_weight(2)
    victim_believes_suspect_used_for_trafficking = models.BooleanField('Victim suspects this location has been used for trafficking', default=False).set_weight(2)
    victim_believes_not_used_for_trafficking = models.BooleanField('Victim does not believe this location is used for trafficking', default=False)

    associated_with_person = models.NullBooleanField(null=True)
    associated_with_person_value = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return "VIF {}".format(self.victim_interview.vif_number)
