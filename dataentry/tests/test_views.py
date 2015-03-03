from django.test import TestCase
from django_webtest import WebTest
from dataentry.views import SearchFormsMixin
from dataentry.models import InterceptionRecord
from django.core.urlresolvers import reverse

from accounts.tests.factories import *

from accounts.models import Account

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


class VictimInterviewFormViewTests(WebTest):
    
    def setUp(self):
        self.superuser = SuperUserFactory.create()
    
    def test_VictimInterviewForm_create_can_be_viewed(self):
        response = self.app.get(reverse('victiminterview_create'), user=self.superuser)
        self.assertEquals(response.status_code, 200)
    
    def test_VictimInterviewForm_does_not_submit_without_valid_fields_filled_out(self):
        response = self.app.get(reverse('victiminterview_create'), user=self.superuser)
        form = response.form
        form_response = form.submit()
        field_errors = form_response.context['form'].errors
        print(field_errors)