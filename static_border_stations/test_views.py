from django_webtest import WebTest
from django.core.urlresolvers import reverse
import json

from accounts.tests.factories import SuperUserFactory

from static_border_stations.models import *
from dataentry.models import BorderStation


class TestBorderStations(WebTest):
    def setUp(self):
        BorderStation.objects.get_or_create(station_name="Test Station", station_code="TS1")
        self.superuser = SuperUserFactory.create()
        url = reverse("borderstations_update", args=[1])
        self.form = self.app.get(url, user=self.superuser).form
        
    def testUpdateStaff(self):
        print(self.form["staff_set-0-first_name"].value)
        self.form["staff_set-0-first_name"] = "testStaff"
        # TODO: Fill form for Staff and submit then check to see if changed in database
        
    def testUpdateCommitteeMember(self):
        # TODO: Fill form for CommitteeMember and submit then check to see if changed in database
        pass
        
    def testUpdateLocation(self):
        # TODO: Fill form for Location and submit then check to see if changed in database
        pass
        
    # TODO: Test editing borderstation info
    # TODO: Test adding/updating more Staff to borderstation
    # TODO: Test adding/updating more CommitteMembers to borderstation
    # TODO: Test adding/updating more Locations to borderstation