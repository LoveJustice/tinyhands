from django.test import TestCase
from django_webtest import WebTest
from django.core.urlresolvers import reverse

from accounts.tests.factories import *
import ipdb

class BorderStationsCreationTest(WebTest):

	def setUp(self):
		self.superuser = SuperUserFactory.create()
		self.response = self.app.get(reverse('borderstations_create'), user=self.superuser)
		self.form = self.response.form

	def test_border_station_create_view_should_exist(self): 
		self.assertEquals(self.response.status_code, 200)

	def test_border_station_create_view_form_fields_are_empty(self): 
		fields = self.form.fields

		self.assertEquals('', fields['station_name'][0].value)
		self.assertEquals('', fields['station_code'][0].value)
		self.assertEquals('', fields['date_established'][0].value)
		self.assertEquals(False, fields['has_shelter'][0].checked)
		self.assertEquals('', fields['latitude'][0].value)
		self.assertEquals('', fields['longitude'][0].value)

		self.assertEquals('', fields['staff_set-0-first_name'][0].value)
		self.assertEquals('', fields['staff_set-0-last_name'][0].value)
		self.assertEquals('', fields['staff_set-0-email'][0].value)
		self.assertEquals(False, fields['staff_set-0-receives_money_distribution_form'][0].checked)

		self.assertEquals('', fields['committeemember_set-0-first_name'][0].value)
		self.assertEquals('', fields['committeemember_set-0-last_name'][0].value)
		self.assertEquals('', fields['committeemember_set-0-email'][0].value)
		self.assertEquals(False, fields['committeemember_set-0-receives_money_distribution_form'][0].checked)

		self.assertEquals('', fields['location_set-0-name'][0].value)
		self.assertEquals('', fields['location_set-0-latitude'][0].value)
		self.assertEquals('', fields['location_set-0-longitude'][0].value)

	def test_border_station_create_view_form_submission_fails_with_empty_fields(self): 
		form_response = self.form.submit()

		#help blocks tell when a field is required
		help_blocks = form_response.html.findAll('span', { "class" : "help-block" })

		#should be 5 help blocks for the 5 required fields
		self.assertEquals(5, len(help_blocks))