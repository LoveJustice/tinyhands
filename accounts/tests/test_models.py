from django.test import TestCase
from accounts.models import *
from accounts.tests.factories import *
from django.core import mail
from django.conf import settings

class TestDefaultPermissionSet(TestCase):

	def setUp(self):
		self.su_permission_set = SuperUserDesignation.create()

	def test_is_used_by_account(self):
		self.assertEquals(False, self.su_permission_set.is_used_by_accounts())
		su = SuperUserFactory.create()
		self.assertEquals(True, self.su_permission_set.is_used_by_accounts())

	def test_email_accounts(self):
		s1 = SuperUserFactory.create(email="bob@test.com")
		s2 = SuperUserFactory.create(email="joe@test.com")
		alert = AlertFactory.create()
		
		self.su_permission_set.email_accounts(alert)
		self.assertEquals(2, len(mail.outbox))
		
		email = mail.outbox[0]
		self.assertEquals(settings.ADMIN_EMAIL_SENDER, email.from_email)
		self.assertEquals(1, len(email.to))
		self.assertEquals('bob@test.com', email.to[0])
		self.assertEquals('Test Subject', email.subject)
		self.assertEquals('<p>Hello </p>', email.body)
		
		email2 = mail.outbox[1]
		self.assertEquals(settings.ADMIN_EMAIL_SENDER, email2.from_email)
		self.assertEquals(1, len(email2.to))
		self.assertEquals('joe@test.com', email2.to[0])
		self.assertEquals('Test Subject', email2.subject)
		self.assertEquals('<p>Hello </p>', email2.body)
		

class TestAccountManager(TestCase):

	def setUp(self):
		self.account_manager = Account.objects
        
	def test_create_user(self):
		#expect error when given bad email
		with self.assertRaises(ValueError):
			self.account_manager.create_user("")

		#seems these functions don't work and are never used so we may want to delete them -AS
		#self.account_manager.create_user("hello@email.org", "password")
		#self.account_manager.create_superuser("hello@email.org", "password")
		

class TestAccount(TestCase):

	def setUp(self):
		self.user = SuperUserFactory.create(email="bob@test.org", first_name="Bob", last_name="Test")
		
	def test_get_username(self):
		self.assertEquals("bob@test.org", self.user.get_username())

	def test_get_short_name(self):
		self.assertEquals("Bob", self.user.get_short_name())

	def test_get_full_name(self):
		self.assertEquals("Bob Test", self.user.get_full_name())
    
	def test_send_activation_email(self):
		self.user.send_activation_email()
		self.assertEquals(1, len(mail.outbox))
		
		email = mail.outbox[0]
		self.assertEquals(settings.ADMIN_EMAIL_SENDER, email.from_email)
		self.assertEquals(1, len(email.to))
		self.assertEquals('bob@test.org', email.to[0])
		self.assertEquals('Bob, your new Tiny Hands Dreamsuite account is ready!', email.subject)
		
	def test_email_user(self):
		alert = AlertFactory.create()
		self.user.email_user("test", alert );
		self.assertEquals(1, len(mail.outbox))
		
		email = mail.outbox[0]
		self.assertEquals(settings.ADMIN_EMAIL_SENDER, email.from_email)
		self.assertEquals(1, len(email.to))
		self.assertEquals('bob@test.org', email.to[0])
		self.assertEquals('Test Subject', email.subject)
		self.assertEquals('<p>Hello </p>', email.body)
		
class TestAlert(TestCase):
	
	def setUp(self):
		self.su_permission_set = SuperUserDesignation.create()
		self.s1 = SuperUserFactory.create(email="bill@test.com")
		self.s2 = SuperUserFactory.create(email="mike@test.com")
		self.alert = AlertFactory.create(permissions_group=[self.su_permission_set])
		
	def test_email_permissions_set(self):
		self.alert.email_permissions_set()
		
		self.assertEquals(2, len(mail.outbox))
		
		email = mail.outbox[0]
		self.assertEquals(settings.ADMIN_EMAIL_SENDER, email.from_email)
		self.assertEquals(1, len(email.to))
		self.assertEquals('bill@test.com', email.to[0])
		self.assertEquals('Test Subject', email.subject)
		self.assertEquals('<p>Hello </p>', email.body)
		
		email2 = mail.outbox[1]
		self.assertEquals(settings.ADMIN_EMAIL_SENDER, email2.from_email)
		self.assertEquals(1, len(email2.to))
		self.assertEquals('mike@test.com', email2.to[0])
		self.assertEquals('Test Subject', email2.subject)
		self.assertEquals('<p>Hello </p>', email2.body)

class TestSettingManager(TestCase):
	
	def setUp(self):
		self.setting = SettingFactory.create(keyword="k1", value=1, description="Description")
		self.setting_manager = Setting.objects
		
	def test_get_by_keyword(self):
		value = self.setting_manager.get_by_keyword("k1")
		self.assertEquals(1, value)
		
		