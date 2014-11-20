from django.test import TestCase
from django_webtest import WebTest
from django.core.urlresolvers import reverse_lazy, reverse
import json

from accounts.tests.factories import *

from accounts.models import Account, Alert
from dataentry.models import BorderStation

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

class PermissionsTesting(WebTest):
    def setUp(self):
        self.superuser = SuperUserFactory.create()
        self.viewuser = ViewUserFactory.create()
        print(Account.objects.all())

    def test_account_permission_work(self):
        account_list = self.app.get(reverse('account_list'), user=self.superuser)
        self.assertEquals(account_list.status_int, 200)
        print("This is the first test")

        account_list = self.app.get(reverse('account_list'), user=self.viewuser, expect_errors=True)
        self.assertEquals(account_list.status_int, 403)
        print("This is the second test")

        # account_edit = account_list.click('Edit')
        # account_edit.form['email'] = 'dvcolgan@gmail.com'
        # redirect = account_edit.save()
        # self.assertEquals(redirect.status_int, 304)
        # account_list = redirect.follow()

        # original = Account.objects.all()[0]
        # self.client.get(reverse('login'))
        #
        # resp = self.client.get('/portal/dashboard/')
        # self.client.get(reverse('login'))
        # print(resp.status_code)
        # self.assertEqual(resp.status_code, 302)





