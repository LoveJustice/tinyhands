from django.test import TestCase
from django_webtest import WebTest
from django.core.urlresolvers import reverse_lazy, reverse
#import json
from accounts.tests.factories import *
from accounts.models import Account, Alert
#from dataentry.models import BorderStation
import ipdb



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
        self.adduser = AddUserFactory.create()
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
        #print("This is the superuser delete test")

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
        #print("This is the superuser detail IRF test")

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
        #create_borderstation = self.app.get(reverse('borderstations_create'), user=self.superuser)
        #self.assertEquals(create_borderstation.status_int, 200)

    def test_account_permissions_viewuser(self):
        #Ensures a viewuser cannot access the account list.
        account_list = self.app.get(reverse('account_list'), user=self.viewuser, expect_errors=True)
        self.assertEquals(account_list.status_int, 403)

        #Ensures a viewuser cannot access page to create a new account.
        account_create = self.app.get(reverse('account_create'), user=self.viewuser, expect_errors=True)
        self.assertEquals(account_create.status_int, 403)

        #Ensures a viewuser cannot access page to delete an account.
        #account_delete = self.app.get(reverse('account_delete/0'), user=self.viewuser, expect_errors=True)
        #self.assertEquals(account_delete.status_int, 403)
        #print("This is the viewuser cannot delete account test")

        #Ensures a viewuser cannot access the access controls page.
        access_control = self.app.get(reverse('access_control'), user=self.viewuser, expect_errors=True)
        self.assertEquals(access_control.status_int, 403)

        #Ensures a viewuser cannot access the access defaults page.
        access_defaults = self.app.get(reverse('access_defaults'), user=self.viewuser, expect_errors=True)
        self.assertEquals(access_defaults.status_int, 403)

        #Ensures a viewuser can view the list of IRF's.
        view_IRF = self.app.get(reverse('interceptionrecord_list'), user=self.viewuser)
        self.assertEquals(view_IRF.status_int, 200)

        #Ensures a viewuser can view the details of IRF's.
        #detail_IRF = self.app.get(reverse('interceptionrecord_detail'), user=self.viewuser)
        #self.assertEquals(detail_IRF.status_int, 200)
        #print("This is the viewuser detail IRF test")

        #Ensures a viewuser cannot create an IRF.
        create_IRF = self.app.get(reverse('interceptionrecord_create'), user=self.viewuser, expect_errors=True)
        self.assertEquals(create_IRF.status_int, 403)

        #Ensures a viewuser can view the list of VIF's.
        view_VIF = self.app.get(reverse('victiminterview_list'), user=self.viewuser)
        self.assertEquals(view_VIF.status_int, 200)

        #Ensures a viewuser cannot access the VDC administrator page.
        vdc_admin = self.app.get(reverse('vdc_admin_page'), user=self.viewuser, expect_errors=True)
        self.assertEquals(vdc_admin.status_int, 403)

        #Ensures a viewuser cannot create a VDC.
        vdc_create = self.app.get(reverse('vdc_create_page'), user=self.viewuser, expect_errors=True)
        self.assertEquals(vdc_create.status_int, 403)

        #Ensures a viewuser can view the main dashboard.
        dashboard = self.app.get(reverse('main_dashboard'), user=self.viewuser)
        self.assertEquals(dashboard.status_int, 200)

        #Ensures a viewuser cannot create a border station.
        create_borderstation = self.app.get(reverse('borderstations_create'), user=self.viewuser, expect_errors=True)
        self.assertEquals(create_borderstation.status_int, 403)

    def test_account_permissions_adduser(self):
        #Ensures an adduser cannot access the account list.
        account_list = self.app.get(reverse('account_list'), user=self.adduser, expect_errors=True)
        self.assertEquals(account_list.status_int, 403)

        #Ensures an adduser cannot access page to create a new account.
        account_create = self.app.get(reverse('account_create'), user=self.adduser, expect_errors=True)
        self.assertEquals(account_create.status_int, 403)

        #Ensures an adduser cannot access page to delete an account.
        #account_delete = self.app.get(reverse('account_delete/0'), user=self.adduser, expect_errors=True)
        #self.assertEquals(account_delete.status_int, 403)
        #print("This is the adduser cannot delete account test")

        #Ensures an adduser cannot access the access controls page.
        access_control = self.app.get(reverse('access_control'), user=self.adduser, expect_errors=True)
        self.assertEquals(access_control.status_int, 403)

        #Ensures an adduser cannot access the access defaults page.
        access_defaults = self.app.get(reverse('access_defaults'), user=self.adduser, expect_errors=True)
        self.assertEquals(access_defaults.status_int, 403)

        #Ensures an adduser can view the list of IRF's.
        view_IRF = self.app.get(reverse('interceptionrecord_list'), user=self.adduser)
        self.assertEquals(view_IRF.status_int, 200)

        #Ensures an adduser can view the details of IRF's.
        #detail_IRF = self.app.get(reverse('interceptionrecord_detail'), user=self.adduser)
        #self.assertEquals(detail_IRF.status_int, 200)
        #print("This is the adduser detail IRF test")

        #Ensures an adduser can create an IRF.
        create_IRF = self.app.get(reverse('interceptionrecord_create'), user=self.adduser)
        self.assertEquals(create_IRF.status_int, 200)

        #Ensures an adduser can view the list of VIF's.
        view_VIF = self.app.get(reverse('victiminterview_list'), user=self.adduser)
        self.assertEquals(view_VIF.status_int, 200)

        #Ensures an adduser cannot access the VDC administrator page.
        vdc_admin = self.app.get(reverse('vdc_admin_page'), user=self.adduser, expect_errors=True)
        self.assertEquals(vdc_admin.status_int, 403)

        #Ensures an adduser can create a VDC.
        vdc_create = self.app.get(reverse('vdc_create_page'), user=self.adduser)
        self.assertEquals(vdc_create.status_int, 200)

        #Ensures a viewuser can view the main dashboard.
        dashboard = self.app.get(reverse('main_dashboard'), user=self.adduser)
        self.assertEquals(dashboard.status_int, 200)

        #Ensures a viewuser can create a border station.
        #create_borderstation = self.app.get(reverse('borderstations_create'), user=self.adduser)
        #self.assertEquals(create_borderstation.status_int, 200)

    def test_account_actions(self):
        pass
        #Consider using the ideas written below by Colgan.

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

class CreateAccountTests(WebTest):
    
    def setUp(self):
        self.viewuser = ViewUserFactory.create(email="lame@sauce.com", first_name="lame", last_name="sauce")
        self.superuser = SuperUserFactory.create(email="super@user.com", first_name="Super", last_name="User")
    
    def test_admin_can_access_create_account_page(self):
        response = self.app.get(reverse('account_create'), user=self.superuser)
        self.assertEquals(200, response.status_code)
    
    def test_view_user_can_not_access_create_account_page(self):
        response = self.app.get(reverse('account_create'), user=self.viewuser, expect_errors=True)
        self.assertEqual(403, response.status_code)
    
    def test_admin_can_create_account(self):
        response = self.app.get(reverse('account_create'), user=self.superuser)
        form = response.form
        form.set('email', 'bob@joe.com')
        form.set('first_name', 'bob')
        form.set('last_name', 'joe')
        form.set('user_designation', 2) #summer intern
        form.set('permission_irf_view', True)
        form.set('permission_irf_add', False)
        form.set('permission_irf_edit', False)
        form.set('permission_vif_view', True)
        form.set('permission_vif_edit', False)
        form.set('permission_vif_add', False)
        form.set('permission_vif_view', False)
        form.set('permission_border_stations_view', True)
        form.set('permission_border_stations_add', False)
        form.set('permission_border_stations_edit', False)
        form.set('permission_receive_email', False)
        form.set('permission_vdc_manage', False)
        
        form_response = form.submit()
        self.assertEquals(302, form_response.status_code)
        
    def test_if_user_was_actually_added_to_db(self):
        response = self.app.get(reverse('account_create'), user=self.superuser)
        form = response.form
        form.set('email', 'bob@joe.com')
        form.set('first_name', 'bob')
        form.set('last_name', 'joe')
        form.set('user_designation', 2) #summer intern
        form.set('permission_irf_view', True)
        form.set('permission_irf_add', False)
        form.set('permission_irf_edit', False)
        form.set('permission_vif_view', True)
        form.set('permission_vif_edit', False)
        form.set('permission_vif_add', False)
        form.set('permission_vif_view', False)
        form.set('permission_border_stations_view', True)
        form.set('permission_border_stations_add', False)
        form.set('permission_border_stations_edit', False)
        form.set('permission_receive_email', False)
        form.set('permission_vdc_manage', False)
        
        form_response = form.submit()
        
        newuser = Account.objects.get(email='bob@joe.com')
        self.assertIsNotNone(newuser)
        
    def test_if_required_fields_are_filled_in(self):
        response = self.app.get(reverse('account_create'), user=self.superuser)
        form = response.form
        form.set('email', 'bob@joe.com')
        form.set('first_name', 'bob')
        form.set('last_name', 'joe')asda
        form.set('user_designation', 2) #summer intern
        form.set('permission_irf_view', True)
        form.set('permission_irf_add', False)
        form.set('permission_irf_edit', False)
        form.set('permission_vif_view', True)
        form.set('permission_vif_edit', False)
        form.set('permission_vif_add', False)
        form.set('permission_vif_view', False)
        form.set('permission_border_stations_view', True)
        form.set('permission_border_stations_add', False)
        form.set('permission_border_stations_edit', False)
        form.set('permission_receive_email', False)
        form.set('permission_vdc_manage', False)
        
        form_response = form.submit()
        
        newuser = Account.objects.get(email='bob@joe.com')
        self.assertIsNotNone(newuser)
        
class UpdatingInformationTests(WebTest):

    def setUp(self):
        self.superuser = SuperUserFactory.create(email="joe@test.org", first_name="Joe", last_name="Test")

        #second user to test duplicate email failure
        self.superuser2 = SuperUserFactory.create(email="joe2@test.org", first_name="Joe", last_name="Test")

        #create user designation so that there are 2 options in user designation select box
        self.viewuserdesignation = ViewUserDesignation.create()

    def test_account_update_view_exists(self):
        response = self.app.get(reverse('account_update', kwargs={'pk': self.superuser.id}), user=self.superuser)
        self.assertEquals(200, response.status_code)

    def test_account_update_view_has_correct_information(self):
        response = self.app.get(reverse('account_update', kwargs={'pk': self.superuser.id}), user=self.superuser)
        form = response.form
        self.assertEquals("joe@test.org", form.get('email').value)
        self.assertEquals("Joe", form.get('first_name').value)
        self.assertEquals("Test", form.get('last_name').value)
        self.assertEquals(True, form.get('user_designation').options[1][1])
        self.assertEquals(True, form.get('permission_irf_view').checked)
        self.assertEquals(True, form.get('permission_irf_add').checked)
        self.assertEquals(True, form.get('permission_irf_edit').checked)
        self.assertEquals(True, form.get('permission_vif_view').checked)
        self.assertEquals(True, form.get('permission_vif_add').checked)
        self.assertEquals(True, form.get('permission_vif_edit').checked)
        self.assertEquals(True, form.get('permission_border_stations_view').checked)
        self.assertEquals(True, form.get('permission_border_stations_add').checked)
        self.assertEquals(True, form.get('permission_border_stations_edit').checked)
        self.assertEquals(True, form.get('permission_accounts_manage').checked)
        self.assertEquals(True, form.get('permission_receive_email').checked)
        self.assertEquals(True, form.get('permission_vdc_manage').checked)
        
    def test_account_update_view_submission_fails_with_missing_required_fields(self):
        response = self.app.get(reverse('account_update', kwargs={'pk': self.superuser.id}), user=self.superuser)
        form = response.form

        form.set('email', '')
        form.set('user_designation', '')
        form_response = form.submit()

        self.assertEquals(200, form_response.status_code)

        field_errors = form_response.context['form'].errors
        self.assertEquals('This field is required.',field_errors['email'][0])
        self.assertEquals('This field is required.',field_errors['user_designation'][0])

    def test_account_update_view_submission_fails_with_duplicate_email(self):
        response = self.app.get(reverse('account_update', kwargs={'pk': self.superuser.id}), user=self.superuser)
        form = response.form

        form.set('email', 'joe2@test.org')
        form_response = form.submit()

        self.assertEquals(200, form_response.status_code)

        field_errors = form_response.context['form'].errors
        self.assertEquals('Account with this Email already exists.', field_errors['email'][0])

    def test_account_update_view_submission_succeeds_with_valid_fields(self):
        response = self.app.get(reverse('account_update', kwargs={'pk': self.superuser.id}), user=self.superuser)
        form = response.form

        form.set('first_name', 'NewJoe')
        form.set('last_name', 'Test2')
        form.set('email', 'newjoe@test.org')
        form.set('user_designation', self.viewuserdesignation.id) #switch to view user designation
        form.set('permission_irf_view', False)
        form.set('permission_irf_add', False)
        form.set('permission_irf_edit', False)
        form.set('permission_vif_view', False)
        form.set('permission_vif_add', False)
        form.set('permission_vif_edit', False)
        form.set('permission_border_stations_view', False)
        form.set('permission_border_stations_add', False)
        form.set('permission_border_stations_edit', False)
        form.set('permission_receive_email', False)
        form.set('permission_vdc_manage', False)

        form_response = form.submit()
        self.assertEquals(302, form_response.status_code)

        response2 = form_response.follow()
        self.assertEquals(200, response2.status_code)

        updatedAccount = Account.objects.get(first_name='NewJoe')
        self.assertEquals('newjoe@test.org', updatedAccount.email)
        self.assertEquals('NewJoe', updatedAccount.first_name)
        self.assertEquals('Test2', updatedAccount.last_name)
        self.assertEquals(self.viewuserdesignation.id, updatedAccount.user_designation_id)
        self.assertEquals(False, updatedAccount.permission_irf_view)
        self.assertEquals(False, updatedAccount.permission_irf_add)
        self.assertEquals(False, updatedAccount.permission_irf_edit)
        self.assertEquals(False, updatedAccount.permission_vif_view)
        self.assertEquals(False, updatedAccount.permission_vif_add)
        self.assertEquals(False, updatedAccount.permission_vif_edit)
        self.assertEquals(False, updatedAccount.permission_border_stations_view)
        self.assertEquals(False, updatedAccount.permission_border_stations_add)
        self.assertEquals(False, updatedAccount.permission_border_stations_edit)
        self.assertEquals(True, updatedAccount.permission_accounts_manage)
        self.assertEquals(False, updatedAccount.permission_receive_email)
        self.assertEquals(False, updatedAccount.permission_vdc_manage)
