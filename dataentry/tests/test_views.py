from django.test import TestCase
from django_webtest import WebTest
from dataentry.views import SearchFormsMixin
from dataentry.models import InterceptionRecord
from django.core.urlresolvers import reverse

from accounts.tests.factories import *

from dataentry.models import BorderStation
from accounts.models import Account

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

	def setUp(self):
		self.superuser = SuperUserFactory.create()
		self.response = self.app.get(reverse('interceptionrecord_create'), user=self.superuser)
		self.form = self.response.form

	def test_irf_number_matches_existing_border_station(self):
		form = self.form

		irfNumber = "BHD123"

		form.set("irf_number", irfNumber)

		#self.assertTrue(False) # TODO: Validate IRF# contains code for existing borderstation
        
    # TODO: Validate IRF# is valid
    # TODO: If IRF# isnt valid do something
    # TODO: Dont let submit if IRF# isnt valid