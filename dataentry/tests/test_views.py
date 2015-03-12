from django.test import TestCase
from django_webtest import WebTest
from dataentry.views import SearchFormsMixin
from dataentry.models import InterceptionRecord
from django.core.urlresolvers import reverse

from accounts.tests.factories import *
from dataentry.tests.factories import IntercepteeFactory

from dataentry.models import BorderStation, Interceptee
from accounts.models import Account
import json

import ipdb

import ipdb

class SearchFormsMixinTests(TestCase):

	def test_constructor(self):

		mixin = SearchFormsMixin(irf_number__icontains="number", staff_name__icontains="name")

		self.assertEqual(mixin.Name,'staff_name__icontains')
		self.assertEqual(mixin.Number, 'irf_number__icontains')


class InterceptionRecordListViewTests(WebTest):

	def setUp(self):
		self.superuser = SuperUserFactory.create()
		self.response = self.app.get(reverse('interceptionrecord_list'), user=self.superuser)
		#self.form = self.response.form

	def test_InterceptionRecordListView_exists(self):
		self.assertEquals(self.response.status_code, 200)

	def test_search_url_exists(self):
		response = self.app.get('/data-entry/irfs/search/?search_value=BHD', user=self.superuser)
		self.assertEquals(response.status_code, 200)


class VictimInterviewFormListViewTests(WebTest):

	def setUp(self):
		self.superuser = SuperUserFactory.create()

	def test_InterceptionRecordListView_exists(self):
		response = self.app.get(reverse('victiminterview_list'), user=self.superuser)
		self.assertEquals(response.status_code, 200)

	def test_search_url_exists(self):
		response = self.app.get('/data-entry/vifs/search/?search_value=BHD', user=self.superuser)
		self.assertEquals(response.status_code, 200)

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
    
class IdentityMatchingViewTests(WebTest):
    
	def setUp(self):
		self.fuzzy_limit = SettingFactory.create(keyword="Fuzzy-Limit", value=5, description="fuzzy limit")
		self.fuzzy_score_cutoff = SettingFactory.create(keyword="Fuzzy-Score-Cutoff", value=50, description="fuzzy score cutoff")
		self.fuzzy_age_weight = SettingFactory.create(keyword="Fuzzy-Age-Weight", value=1, description="fuzzy age weight")
		self.fuzzy_phone_weight = SettingFactory.create(keyword="Fuzzy-Phone-Number-Weight", value=1, description="fuzzy phone number weight")
		self.interceptee = IntercepteeFactory.create(name="Matt",age=20,phone='1234567890')
		self.interceptee2 = IntercepteeFactory.create(name="Bob",age=35,phone='1112223333')
		self.superuser = SuperUserFactory.create()

	def test_when_no_parameters_returns_error(self):
		response = self.app.get(reverse('interceptee_fuzzy_matching'), user=self.superuser)
		
		self.assertEqual(response.body, '{"data": "You must pass at least one parameter", "success": false}')
		
	def test_get_matches_with_just_name(self):
		response = self.app.get(reverse('interceptee_fuzzy_matching'), params={'name': "Matt"}, user=self.superuser)
		body = json.loads(response.body);
		
		self.assertEqual("Matt", body['data'][0][1][0]);
	
	def test_get_matches_with_just_age(self):
		response = self.app.get(reverse('interceptee_fuzzy_matching'), params={'age': "20"}, user=self.superuser)
		body = json.loads(response.body);
		
		self.assertEqual("Matt", body['data'][0][1][0]);
		
	def test_get_matches_with_just_phone(self):
		response = self.app.get(reverse('interceptee_fuzzy_matching'), params={'phone': "1234567890"}, user=self.superuser)
		body = json.loads(response.body);
		
		self.assertEqual("Matt", body['data'][0][1][0]);
		
	def test_get_matches_with_name_phone_age(self):
		response = self.app.get(reverse('interceptee_fuzzy_matching'), params={'phone': "1234567890",'name': "Matt", 'age': "20"}, user=self.superuser)
		body = json.loads(response.body);
		
		self.assertEqual("Matt", body['data'][0][1][0]);
		
class MatchingModalTests(WebTest):
    
	def setUp(self):
		self.fuzzy_limit = SettingFactory.create(keyword="Fuzzy-Limit", value=5, description="fuzzy limit")
		self.fuzzy_score_cutoff = SettingFactory.create(keyword="Fuzzy-Score-Cutoff", value=50, description="fuzzy score cutoff")
		self.fuzzy_age_weight = SettingFactory.create(keyword="Fuzzy-Age-Weight", value=1, description="fuzzy age weight")
		self.fuzzy_phone_weight = SettingFactory.create(keyword="Fuzzy-Phone-Number-Weight", value=1, description="fuzzy phone number weight")
		self.interceptee = IntercepteeFactory.create(name="Matt",age=20,phone='1234567890')
		self.interceptee.save()
		self.interceptee2 = IntercepteeFactory.create(name="Bob",age=35,phone='1112223333')
		self.interceptee2.save()
		self.superuser = SuperUserFactory.create()

	def test_when_no_id_returns_error(self):
		response = self.app.get(reverse('matching_modal', kwargs={'id': ''}), user=self.superuser)

		self.assertEqual(response.body, "You must pass parameter 'id'<br/>Example: /matching_modal/1")
		
	
	def test_when_get_with_name_returns_modal(self):
		response = self.app.get(reverse('matching_modal', kwargs={'id': self.interceptee.id}), params={'name': "Matt"}, user=self.superuser)
		
		self.assertEquals(response.status_code, 200);
		self.assertEquals(response.template.name, "dataentry/matching_modal.html")
		
	def test_when_get_with_age_returns_modal(self):
		response = self.app.get(reverse('matching_modal', kwargs={'id': self.interceptee.id}), params={'age': 20}, user=self.superuser)
		
		self.assertEquals(response.status_code, 200);
		self.assertEquals(response.template.name, "dataentry/matching_modal.html")
		
	def test_when_get_with_phone_returns_modal(self):
		response = self.app.get(reverse('matching_modal', kwargs={'id': self.interceptee.id}), params={'phone': "1234567890"}, user=self.superuser)
		
		self.assertEquals(response.status_code, 200);
		self.assertEquals(response.template.name, "dataentry/matching_modal.html")
		
	def test_when_post_with_create_and_values_changes_interceptee_info(self):
		response = self.app.post(reverse('matching_modal', kwargs={'id': self.interceptee.id}), params={'canonical_name[create]': "true", 'canonical_name[value]': "Bill",'canonical_age[create]':'true','canonical_age[value]':'27','canonical_phone[create]': "true",'canonical_phone[value]': "2223334444"}, user=self.superuser)
		
		self.assertEquals(response.status_code, 200);
		self.assertEquals(response.body, '{"phone": "2223334444", "age": "27", "name": "Bill"}')
		
		person = Interceptee.objects.get(id=self.interceptee.id);

		self.assertEquals(person.canonical_name.value, "Bill")
		self.assertEquals(person.canonical_age.value, 27)
		self.assertEquals(person.canonical_phone.value, "2223334444")
		
	def test_when_post_with_no_create_and_values_changes_interceptee_info(self):
		name_id = self.interceptee2.canonical_name_id
		age_id = self.interceptee2.canonical_age_id
		phone_id = self.interceptee2.canonical_phone_id
		
		response = self.app.post(reverse('matching_modal', kwargs={'id': self.interceptee.id}), params={'canonical_name[create]': "false", 'canonical_name[value]': name_id,'canonical_age[create]':'false','canonical_age[value]':age_id,'canonical_phone[create]': "false",'canonical_phone[value]': phone_id}, user=self.superuser)
		self.assertEquals(response.status_code, 200);
		
		person = Interceptee.objects.get(id=self.interceptee.id);

		self.assertEquals(person.canonical_name.value, self.interceptee2.canonical_name.value)
		self.assertEquals(person.canonical_age.value, self.interceptee2.canonical_age.value)
		self.assertEquals(person.canonical_phone.value, self.interceptee2.canonical_phone.value)
