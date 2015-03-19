from django.test import TestCase
from django_webtest import WebTest
from dataentry.views import SearchFormsMixin
from dataentry.models import InterceptionRecord
from django.core.urlresolvers import reverse
from accounts.tests.factories import *
from dataentry.models import BorderStation, Interceptee
from accounts.models import Account


class InterceptionRecordCreateViewTests(WebTest):
	fixtures = ['accounts.json','portal/border_stations.json']
	
	def setUp(self):
		self.superuser = SuperUserFactory.create()
		url = reverse("interceptionrecord_create")
		self.response = self.app.get(url, user=self.superuser)
		self.form = self.response.form
		
	def test_irf_number_is_valid(self):
		form = self.form
		form.set('irf_number', BorderStation.objects.all()[0].station_code + '123')
		BSCode = form.get("irf_number").value[:3]
		self.assertEqual(3, len(BSCode))
		
	def test_irf_number_matches_existing_border_station(self):
		form = self.form
		form.set('irf_number', BorderStation.objects.all()[0].station_code + '123')
		BSCode = form.get("irf_number").value[:3]
		borderstation = BorderStation.objects.all().filter(station_code=BSCode)
		self.assertNotEqual(0, len(borderstation))
		
	def test_when_irf_number_is_invalid_fail_to_submit_with_errors(self):
		form = self.form
		form.set('irf_number', '123')
		form_response = form.submit()
		theErrors = form_response.context['form'].errors
		self.assertIn('irf_number', theErrors.keys())
		self.assertIsNotNone(theErrors['irf_number'])


class VictimInterviewFormCreateViewTests(WebTest):
	fixtures = ['accounts.json','portal/border_stations.json']
	
	def setUp(self):
		self.superuser = SuperUserFactory.create()
		url = reverse("victiminterview_create")
		self.response = self.app.get(url, user=self.superuser)
		self.form = self.response.form
		
	def test_vif_number_is_valid(self):
		form = self.form
		form.set('vif_number', BorderStation.objects.all()[0].station_code + '123')
		BSCode = form.get("vif_number").value[:3]
		self.assertEqual(3, len(BSCode))
		
	def test_vif_number_matches_existing_border_station(self):
		form = self.form
		form.set('vif_number', BorderStation.objects.all()[0].station_code + '123')
		BSCode = form.get("vif_number").value[:3]
		borderstation = BorderStation.objects.all().filter(station_code=BSCode)
		self.assertNotEqual(0, len(borderstation))
		
	def test_when_vif_number_is_invalid_fail_to_submit_with_errors(self):
		form = self.form
		form.set('vif_number', '123')
		form_response = form.submit()
		theErrors = form_response.context['form'].errors
		self.assertIn('vif_number', theErrors.keys())
		self.assertIsNotNone(theErrors['vif_number'])