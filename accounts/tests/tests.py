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
        #print(Account.objects.all())

    def test_account_permissions_superuser(self):
        #Ensures a superuser can access the account list.
        account_list = self.app.get(reverse('account_list'), user=self.superuser)
        self.assertEquals(account_list.status_int, 200)

        #Ensures a superuser can access page to create a new account.
        account_create = self.app.get(reverse('account_create'), user=self.superuser)
        self.assertEquals(account_create.status_int, 200)

        #Ensures a superuser can access page to delete an account.
        #account_delete = self.app.get(reverse('account_delete/0'), user=self.superuser)
        #self.assertEquals(account_delete.status_int, 200)
        #print("This is the delete test")

        #Ensures a superuser can access the access controls page.
        access_control = self.app.get(reverse('access_control'), user=self.superuser)
        self.assertEquals(access_control.status_int, 200)

        #Ensures a superuser can access the access defaults page.
        access_defaults = self.app.get(reverse('access_defaults'), user=self.superuser)
        self.assertEquals(access_defaults.status_int, 200)

        #Ensures a superuser can view the list of IRF's.
        view_IRF = self.app.get(reverse('interceptionrecord_list'), user=self.superuser)
        self.assertEquals(view_IRF.status_int, 200)

        #Ensures a superuser can view the details of IRF's.
        #detail_IRF = self.app.get(reverse('interceptionrecord_detail'), user=self.superuser)
        #self.assertEquals(detail_IRF.status_int, 200)
        #print("This is the detail IRF test")

        #Ensures a superuser can create an IRF.
        create_IRF = self.app.get(reverse('interceptionrecord_create'), user=self.superuser)
        self.assertEquals(create_IRF.status_int, 200)

        #Ensures a superuser can view the list of VIF's.
        view_VIF = self.app.get(reverse('victiminterview_list'), user=self.superuser)
        self.assertEquals(view_VIF.status_int, 200)

        #Ensures a superuser can access the VDC administrator page.
        vdc_admin = self.app.get(reverse('vdc_admin_page'), user=self.superuser)
        self.assertEquals(vdc_admin.status_int, 200)

        #Ensures a superuser can create a VDC.
        vdc_create = self.app.get(reverse('vdc_create_page'), user=self.superuser)
        self.assertEquals(vdc_create.status_int, 200)

        #Ensures a superuser can view the main dashboard.
        dashboard = self.app.get(reverse('main_dashboard'), user=self.superuser)
        self.assertEquals(dashboard.status_int, 200)

        #Ensures a superuser can create a border station.
        create_borderstation = self.app.get(reverse('borderstations_create'), user=self.superuser)
        self.assertEquals(create_borderstation.status_int, 200)
        #print("This is the create border stations test")

    def test_account_permissions_viewuser(self):
        #Ensures a viewuser cannot access the account list.
        account_list = self.app.get(reverse('account_list'), user=self.viewuser, expect_errors=True)
        self.assertEquals(account_list.status_int, 403)

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





