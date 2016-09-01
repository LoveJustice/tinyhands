from unittest import TestCase

from django.core.urlresolvers import reverse
from accounts.tests.factories import SuperUserFactory

from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework import status
from dataentry.models.site_settings import SiteSettings
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

class SiteSettingsTests(APITestCase):
    def setUp(self):
        self.site_settings = SiteSettingsFactory.create()

    def test_site_settings_structure(self):
        self.assertIsNotNone(self.site_settings.data)

