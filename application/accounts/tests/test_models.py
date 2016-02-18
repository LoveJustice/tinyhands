from django.test import TestCase
from accounts.models import *
from accounts.tests.factories import *


class TestDefaultPermissionSet(TestCase):

    def setUp(self):
        self.su_permission_set = SuperUserDesignation.create()

    def test_is_used_by_account(self):
        self.assertEquals(False, self.su_permission_set.is_used_by_accounts())
        SuperUserFactory.create()
        self.assertEquals(True, self.su_permission_set.is_used_by_accounts())

    def test_email_accounts(self):
        pass


class TestAccountManager(TestCase):

    def setUp(self):
        self.account_manager = AccountManager()

    def test_create_user(self):
        # expect error when given bad email
        with self.assertRaises(ValueError):
            self.account_manager.create_user("")

        # TODO see what account manager is used for
        # errors on self.model() because model is undefined
        # self.account_manager.create_user("hello", "password", name="Bob")


class TestAccount(TestCase):

    def setUp(self):
        self.user = SuperUserFactory.create(email="bob@test.org", first_name="Bob", last_name="Test")

    def test_get_username(self):
        self.assertEquals("bob@test.org", self.user.get_username())

    def test_get_short_name(self):
        self.assertEquals("Bob", self.user.get_short_name())

    def test_get_full_name(self):
        self.assertEquals("Bob Test", self.user.get_full_name())
