from unittest import TestCase

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
import datetime

from accounts.tests.factories import SuperUserFactory, BadIrfUserFactory
from dataentry.tests.factories import SiteSettingsFactory


class SiteSettingsTest(TestCase):
    def setUp(self):
        self.site_settings = SiteSettingsFactory.create()

    def test_get_setting_value_by_name__valid_setting_name(self):
        # {'name': 'address1_cutoff', 'value': 70, 'description': "asdfasdf"},
        value = self.site_settings.get_setting_value_by_name('address1_cutoff')
        self.assertEqual(value, 70)

    def test_get_setting_value_by_name__invalid_setting_name(self):
        self.assertRaises(ValueError, self.site_settings.get_setting_value_by_name, 'address4_cutoff')

    def test_get_setting_by_name(self):
        setting = self.site_settings.get_setting_by_name("address1_cutoff")
        self.assertIsNotNone(setting)
        self.assertEquals(setting['name'], "address1_cutoff")
        self.assertEquals(setting['value'], 70)
        self.assertEquals(setting['description'], "asdfasdf")

    def test_get_setting_by_name__invalid_setting_name(self):
        self.assertRaises(ValueError, self.site_settings.get_setting_by_name, 'address4_cutoff')

    def test_date_updated_gets_autoupdated(self):
        tmp = self.site_settings.date_time_last_updated
        self.site_settings.save()
        self.assertNotEquals(tmp, self.site_settings.date_time_last_updated)

    def test_site_settings_structure(self):
        self.assertIsNotNone(self.site_settings.data)


class SiteSettingsApiTests(APITestCase):
    def setUp(self):
        self.site_settings = SiteSettingsFactory.create()

    def test_superuser_are_authenticated(self):
        self.user = SuperUserFactory.create()
        self.client.force_authenticate(user=self.user)

        # get
        url = reverse('SiteSettings')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # put detail
        data = {"data": '{"hello": "1"}', "date_time_last_updated": "2016-09-17T19:54:08.820420Z"}
        url = reverse('SiteSettingsUpdate', args=[self.site_settings.id])
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"], data["data"])

    def test_unauthenticated_not_allowed(self):
        self.bad_user = BadIrfUserFactory.create()
        self.client.force_authenticate(user=self.bad_user)

        # get
        url = reverse('SiteSettings')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # put detail
        url = reverse('SiteSettingsUpdate', args=[self.site_settings.id])
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
