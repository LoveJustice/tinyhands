from django.test import TestCase
from django_webtest import WebTest
from django.core.urlresolvers import reverse
import json

from accounts.tests.factories import *

from accounts.models import Account
from dataentry.models import BorderStation

# Create your tests here.
class BorderStationModelsTests(WebTest):
    
    def setUp(self):
        BorderStation.objects.get_or_create(station_name="Test Station", station_code="TS1")
        self.superuser = SuperUserFactory.create()
        self.adduser = AddUserFactory.create()
        self.viewuser = ViewUserFactory.create()
        
    # Ensure proper Superuser Permissions
    def test_can_get_create_borderstation_page_as_superuser(self):
        url = reverse("borderstations_create")
        page = self.app.get(url, user=self.superuser)
        self.assertEquals(page.status_int, 200)
        
    def test_can_get_update_borderstation_page_as_superuser(self):
        url = reverse("borderstations_update", args=[1])
        page = self.app.get(url, user=self.superuser)
        self.assertEquals(page.status_int, 200)
        
    def test_can_get_view_borderstation_page_as_superuser(self):
        url = reverse("borderstations_view", args=[1])
        page = self.app.get(url, user=self.superuser)
        self.assertEquals(page.status_int, 200)
        
    def test_superuser_borderstation_create(self):
        url = reverse("borderstations_create")
        form = self.app.get(url, user=self.superuser).form
        print(form)
        
    # Ensure proper Adduser Permissions
    def test_can_get_create_borderstation_page_as_adduser(self):
        url = reverse("borderstations_create")
        page = self.app.get(url, user=self.adduser)
        self.assertEquals(page.status_int, 200)
        
    def test_can_get_update_borderstation_page_as_adduser(self):
        url = reverse("borderstations_update", args=[1])
        page = self.app.get(url, user=self.adduser, expect_errors=True)
        self.assertEquals(page.status_int, 403)
        
    def test_can_get_view_borderstation_page_as_adduser(self):
        url = reverse("borderstations_view", args=[1])
        page = self.app.get(url, user=self.adduser)
        self.assertEquals(page.status_int, 200)
        
    # Ensure proper Viewuser Permissions
    def test_cannot_get_create_borderstation_page_as_viewuser(self):
        url = reverse("borderstations_create")
        page = self.app.get(url, user=self.viewuser, expect_errors=True)
        self.assertEquals(page.status_int, 403)
        
    def test_can_get_update_borderstation_page_as_viewuser(self):
        url = reverse("borderstations_update", args=[1])
        page = self.app.get(url, user=self.viewuser, expect_errors=True)
        self.assertEquals(page.status_int, 403)
        
    def test_can_get_view_borderstation_page_as_viewuser(self):
        url = reverse("borderstations_view", args=[1])
        page = self.app.get(url, user=self.viewuser)
        self.assertEquals(page.status_int, 200)