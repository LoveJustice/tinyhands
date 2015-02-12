from django_webtest import WebTest
from django.utils.unittest import TestCase 
from accounts.models import Account, Alert


class TestModels(TestCase):
    def setUp(self):
        self.account = Account()
        

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

