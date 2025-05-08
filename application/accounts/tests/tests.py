import unittest

from accounts.models import Alert, Account
from accounts.tests.factories import SuperUserFactory
from django.core import mail


class AlertTestCase(unittest.TestCase):
    def setUp(self):
        self.alert = Alert(1, 'code', 'template')
        self.alert.save()

    def testAlertAdded(self):
        x = Alert.objects.all()
        self.assertEqual(len(x), 1)

    def testAlertRemoved(self):
        x = Alert.objects.all()[0]  # get the first alert in the database
        x.delete()
        self.assertEqual(len(Alert.objects.all()), 0)


class AccountTest(unittest.TestCase):
    def test_unicode(self):
        account = SuperUserFactory.create()

        result = str(account)

        self.assertEqual(result, account.email)

    def test_get_username(self):
        account = SuperUserFactory.create()

        result = account.get_username()

        self.assertEqual(result, account.email)

    def test_get_short_name(self):
        account = SuperUserFactory.create()

        result = account.get_short_name()

        self.assertEqual(result, account.first_name)

    def test_get_full_name(self):
        account = SuperUserFactory.create()

        result = account.get_full_name()

        self.assertEqual(result, account.first_name+' '+account.last_name)

    def test_email_user(self):
        account = SuperUserFactory.create()
        subject = "foo"

        account.email_user("test_templated_email", "alert", {"subject": subject})

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, subject)
        self.assertEqual(mail.outbox[0].to[0], account.email)
