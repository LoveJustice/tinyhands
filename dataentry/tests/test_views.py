from django.test import TestCase
from django_webtest import WebTest
from dataentry.views import SearchFormsMixin
from dataentry.models import InterceptionRecord
from django.core.urlresolvers import reverse

from accounts.tests.factories import *

from accounts.models import Account

import datetime

class SearchFormsMixinTests(TestCase):

	def test_constructor(self):

		mixin = SearchFormsMixin(irf_number__icontains="number", staff_name__icontains="name")

		self.assertEqual(mixin.Name,'staff_name__icontains')
		self.assertEqual(mixin.Number, 'irf_number__icontains')


class InterceptionRecordListViewTests(WebTest):

	def setUp(self):
		self.superuser = SuperUserFactory.create()

	def test_InterceptionRecordListView_exists(self):
		response = self.app.get(reverse('interceptionrecord_list'), user=self.superuser)
		self.assertEquals(response.status_code, 200)

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

class InterceptionRecordFormViewTests(WebTest):
    
    fixture = ['geo-code-locations.json']
    
    def setUp(self):
        self.superuser = SuperUserFactory.create();
        
    def test_user_can_create_irf_form(self):
        pass

    
class VictimInterviewFormViewTests(WebTest):

    fixtures = ['geo-code-locations.json']
    
    def setUp(self):
        self.superuser = SuperUserFactory.create();

    def test_can_user_create_vif_form(self):
        response = self.app.get(reverse('victiminterview_create'), user=self.superuser)
        self.assertEquals(response.status_code, 200)

    def test_form_submits_with_required_fields_and_redirects(self):
        response = self.app.get(reverse('victiminterview_create'), user=self.superuser)
        form = response.form
        form.set('vif_number', 'CND2')
        form.set('date', datetime.datetime.now().strftime("%m/%d/%Y"))
        form.set('interviewer', "johnny be good")
        form.set('statement_read_before_beginning', True);
        form.set('victim_gender', "male")
        form.set('victim_name', "Sally Sue")
        form.set('victim_address_district', "Dhanusa")
        form.set('victim_address_vdc', 'Chalsa')
        form.set('migration_plans_education', True)
        form.set('primary_motivation_support_myself', True)
        form.set('victim_primary_means_of_travel_local_bus', True)
        form.set('victim_guardian_address_district', "Dhanusa")
        form.set('victim_guardian_address_vdc', "Chalsa")
        form.fields['victim_recruited_in_village'][0].checked = True
        form.fields['victim_stayed_somewhere_between'][0].checked = True
        form.set('meeting_at_border_yes', True)
        form.fields['victim_knew_details_about_destination'][0].checked = True
        form.set('awareness_before_interception_had_heard_not_how_bad', True)
        form.set('legal_action_against_traffickers_no', True)
        form.set('attitude_towards_tiny_hands_thankful', True)
        form.set('victim_heard_gospel_no', True)
        form.set('has_signature', True)
        form_response = form.submit()
        field_errors = form_response.context['form'].errors
        form_2 = form_response.form
        form_2.set('ignore_warnings', True)
        form_response_2 = form_2.submit()
        self.assertEquals(form_response_2.status_code, 302)

    def test_form_does_not_submit_without_required_fields(self):
        response = self.app.get(reverse('victiminterview_create'), user=self.superuser)
        form = response.form
        form.set('vif_number', 'CND2')
        form.set('date', datetime.datetime.now().strftime("%m/%d/%Y"))
        form.set('interviewer', "johnny be good")
        form.set('statement_read_before_beginning', True);
        form.set('victim_gender', "male")
        form.set('victim_name', "Sally Sue")
        form.set('victim_address_district', "Dhanusa")
        form.set('victim_address_vdc', 'Chalsa')
        form.set('migration_plans_education', True)
        form.set('primary_motivation_support_myself', True)
        form.set('victim_primary_means_of_travel_local_bus', True)
        form.set('victim_guardian_address_district', "Dhanusa")
        form.set('victim_guardian_address_vdc', "Chalsa")
        form.fields['victim_recruited_in_village'][0].checked = True
        form.fields['victim_stayed_somewhere_between'][0].checked = True
        form.set('meeting_at_border_yes', True)
        form.fields['victim_knew_details_about_destination'][0].checked = True
        form.set('awareness_before_interception_had_heard_not_how_bad', True)
        form.set('legal_action_against_traffickers_no', True)
        form.set('attitude_towards_tiny_hands_thankful', True)
        form.set('victim_heard_gospel_no', True)
        form_response = form.submit()
        field_errors = form_response.context['form'].errors
        self.assertEquals(field_errors['has_signature'][0], "This field is required.")
