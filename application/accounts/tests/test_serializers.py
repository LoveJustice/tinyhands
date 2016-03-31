from django.test import TestCase
from django.db import models
from accounts.serializers import AccountsSerializer
from rest_framework import serializers
from accounts.tests.factories import SuperUserDesignation
from dreamsuite.test_email_backend import SMTP_ERROR_EMAIL

class TestAccountsSerializer(TestCase):
	def setUp(self):
		self.serializer = AccountsSerializer()
		self.SuperUserDesignation = SuperUserDesignation.create()
		self.testUserInfo = {
			"email":"", 
			"first_name":"Jaeger", 
			"last_name":"Manjensen", 
			"user_designation":self.SuperUserDesignation,
			"permission_irf_view": True,
			"permission_irf_add": True,
			"permission_irf_edit": True,
			"permission_irf_delete": True,
			"permission_vif_add": True,
			"permission_vif_view": True,
			"permission_vif_edit": True,
			"permission_vif_delete": True,
			"permission_accounts_manage": True,
			"permission_border_stations_view": True,
			"permission_border_stations_add": True,
			"permission_border_stations_edit": True,
			"permission_address2_manage": True,
			"permission_budget_manage": True,
		}
	
	def test_create_with_valid_email(self):
		self.testUserInfo["email"] = "valid@smtperror.com"
		try:
			account = self.serializer.create(self.testUserInfo)
			account.delete()
		except serializers.ValidationError:
			self.fail()
		self.assertTrue(True)


	def test_create_with_invalid_email(self):
		self.testUserInfo["email"] = SMTP_ERROR_EMAIL
		with self.assertRaises(serializers.ValidationError):
			account = self.serializer.create(self.testUserInfo)
			account.delete()
