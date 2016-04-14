from django.test import TestCase
from django_webtest import WebTest
from django.core.urlresolvers import reverse, resolve
import json

from accounts.tests.factories import *

from accounts.models import Account
from static_border_stations.tests.factories import BorderStationFactory

# Create your tests here.
class BorderStationModelsTests(WebTest):

    def setUp(self):
        self.border_station = BorderStationFactory.create()
        self.superuser = SuperUserFactory.create()
        self.viewuser = ViewUserFactory.create()
        self.adduser = AddUserFactory.create()
        self.edituser = EditUserFactory.create()

    # Ensure proper Superuser Permissions
    def test_can_get_create_borderstation_page_as_superuser(self):
        url = reverse("borderstations_create")
        page = self.app.get(url, user=self.superuser)
        self.assertEquals(page.status_int, 200)

    def test_can_get_update_borderstation_page_as_superuser(self):
        url = reverse("borderstations_update", args=[self.border_station.id])
        page = self.app.get(url, user=self.superuser)
        self.assertEquals(page.status_int, 200)

    def test_can_get_view_borderstation_page_as_superuser(self):
        url = reverse("borderstations_view", args=[self.border_station.id])
        page = self.app.get(url, user=self.superuser)
        self.assertEquals(page.status_int, 200)

    # Ensure proper Viewuser Permissions
    def test_cannot_get_create_borderstation_page_as_viewuser(self):
        url = reverse("borderstations_create")
        page = self.app.get(url, user=self.viewuser, expect_errors=True)
        self.assertEquals(page.status_int, 403)

    def test_cannot_get_update_borderstation_page_as_viewuser(self):
        url = reverse("borderstations_update", args=[self.border_station.id])
        page = self.app.get(url, user=self.viewuser, expect_errors=True)
        self.assertEquals(page.status_int, 403)

    def test_can_get_view_borderstation_page_as_viewuser(self):
        url = reverse("borderstations_view", args=[self.border_station.id])
        page = self.app.get(url, user=self.viewuser)
        self.assertEquals(page.status_int, 200)

    # Ensure proper Adduser Permissions
    def test_can_get_create_borderstation_page_as_adduser(self):
        url = reverse("borderstations_create")
        page = self.app.get(url, user=self.adduser)
        self.assertEquals(page.status_int, 200)

    def test_cannot_get_update_borderstation_page_as_adduser(self):
        url = reverse("borderstations_update", args=[self.border_station.id])
        page = self.app.get(url, user=self.adduser, expect_errors=True)
        self.assertEquals(page.status_int, 403)

    def test_can_get_view_borderstation_page_as_adduser(self):
        url = reverse("borderstations_view", args=[self.border_station.id])
        page = self.app.get(url, user=self.adduser)
        self.assertEquals(page.status_int, 200)

    # Ensure proper Edituser Permissions
    def test_cannot_get_create_borderstation_page_as_edituser(self):
        url = reverse("borderstations_create")
        page = self.app.get(url, user=self.edituser, expect_errors=True)
        self.assertEquals(page.status_int, 403)

    def test_can_get_update_borderstation_page_as_edituser(self):
        url = reverse("borderstations_update", args=[self.border_station.id])
        page = self.app.get(url, user=self.edituser)
        self.assertEquals(page.status_int, 200)

    def test_can_get_view_borderstation_page_as_edituser(self):
        url = reverse("borderstations_view", args=[self.border_station.id])
        page = self.app.get(url, user=self.edituser)
        self.assertEquals(page.status_int, 200)
