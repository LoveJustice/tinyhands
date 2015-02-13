from django.test import TestCase
from django_webtest import WebTest
from django.core.urlresolvers import reverse

from accounts.tests.factories import SuperUserFactory
from dataentry.models import BorderStation

class BorderStationsCreationTest(WebTest):

	def setUp(self):
		self.superuser = SuperUserFactory.create()
		self.response = self.app.get(reverse('borderstations_create'), user=self.superuser)
		self.form = self.response.form
		BorderStation.objects.get_or_create(station_name="Test Station", station_code="TTT")

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

		field_errors = form_response.context['form'].errors

		self.assertEquals(200, form_response.status_code)
		self.assertEquals('This field is required.',field_errors['station_name'][0])
		self.assertEquals('This field is required.',field_errors['station_code'][0])
		self.assertEquals('This field is required.',field_errors['date_established'][0])
		self.assertEquals('This field is required.',field_errors['latitude'][0])
		self.assertEquals('This field is required.',field_errors['longitude'][0])

	def test_border_station_create_view_form_submission_fails_with_dupilicate_station_code(self): 
		form = self.form

		form.set('station_name', 'Station 1')
		form.set('station_code', 'TTT')
		form.set('date_established', '1/1/11')
		form.set('longitude', '3')
		form.set('latitude', '4')
		form_response = form.submit()

		field_errors = form_response.context['form'].errors
		
		self.assertEquals(200, form_response.status_code)
		self.assertEquals('Border station with this Station code already exists.',field_errors['station_code'][0])
		

	def test_border_station_create_view_form_submits_with_correct_fields(self): 
		form = self.form

		form.set('station_name', 'Station 1')
		form.set('station_code', 'STS')
		form.set('date_established', '1/1/11')
		form.set('longitude', '3')
		form.set('latitude', '4')
		form_response = form.submit()

		self.assertEquals(302, form_response.status_code)
		self.assertEquals('', form_response.errors)