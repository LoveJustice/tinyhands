from django_webtest import WebTest
from django.test import TestCase
from accounts.models import Account, Alert


class TestModels(WebTest):
    pass


class AlertTestCase(TestCase):
    def setUp(self):
        self.alert = Alert(1, 'code', 'template')
        self.alert.save()

    def testAlertAdded(self):
        x = Alert.objects.all()
        self.assertEqual(len(x),1)

    def testAlertRemoved(self):
        x = Alert.objects.all()[0] #get the first alert in the database
        x.delete()
        self.assertEqual(len(Alert.objects.all()),0)

class PermissionsTesting(TestCase):

    fixtures = ['accounts.json']

    def test_permissions_overview(self):
        original = Account.objects.all()[0]
        self.client.get(reverse('login'))

        resp = self.client.get('/portal/dashboard/')
        self.client.get(reverse('login'))
        print(resp.status_code)
        self.assertEqual(resp.status_code, 302)





