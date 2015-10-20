from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from accounts.tests.factories import SuperUserFactory, ViewUserFactory

class AccountsTestCase(APITestCase):
    
    def login(self, user):
        self.client = APIClient()
        self.client.force_authenticate(user=user)
    

class AccountsGetTests(AccountsTestCase):
    
    def test_when_not_authenticated_should_deny_access(self):
        url = reverse('Accounts')
        
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_when_authenticated_and_does_not_have_permission_should_deny_access(self):
        url = reverse('Accounts')
        user = ViewUserFactory.create()
        self.login(user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have the right permission to access this data') 

    def test_when_authenticated_and_has_permission_should_return_all_accounts(self):
        url = reverse('Accounts')
        user = SuperUserFactory.create()
        self.login(user)
        
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

class AccountsPostTests(AccountsTestCase):
    
    email = 'foo@bar.org'
    first_name = 'Test'
    last_name = 'Tester'
    new_user = { 
        'email' : email,
        'first_name' : first_name,
        'last_name' : last_name,
        'user_designation' : 1,
        'permission_irf_view' : True,
        'permission_irf_add' : True,
        'permission_irf_edit' : True,
        'permission_irf_delete' : True,
        'permission_vif_view' : True,
        'permission_vif_add' : True,
        'permission_vif_edit' : True,
        'permission_vif_delete' : True,
        'permission_accounts_manage' : True,
        'permission_border_stations_view' : True,
        'permission_border_stations_add' : True,
        'permission_border_stations_edit' : True,
        'permission_vdc_manage' : True,
        'permission_budget_manage' : True,
    }

    def test_when_not_authenticated_should_deny_access(self):
        url = reverse('Accounts')
        
        response = self.client.post(url, self.new_user)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_when_authenticated_and_does_not_have_permission_should_deny_access(self):
        url = reverse('Accounts')
        user = ViewUserFactory.create()
        self.login(user)

        response = self.client.post(url, self.new_user)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have the right permission to access this data')

    def test_when_authenticated_and_has_permission_should_create_account(self):
        url = reverse('Accounts')
        user = SuperUserFactory.create()
        self.login(user)
        
        response = self.client.post(url, self.new_user)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], self.email)
        self.assertEqual(response.data['first_name'], self.first_name)
        self.assertEqual(response.data['last_name'], self.last_name)


class AccountGetTests(AccountsTestCase):
    
    def test_when_not_authenticated_should_deny_access(self):
        user = SuperUserFactory.create()
        url = reverse('Account', args=[user.id])
        
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_when_authenticated_and_does_not_have_permission_should_deny_access(self):
        user = ViewUserFactory.create()
        url = reverse('Account', args=[user.id])
        self.login(user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have the right permission to access this data') 

    def test_when_authenticated_and_has_permission_should_return_account(self):
        user = SuperUserFactory.create()
        url = reverse('Account',args=[user.id])
        self.login(user)
        
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], user.id)
        self.assertEqual(response.data['email'], user.email)


class AccountPutTests(AccountsTestCase):
    
    def get_update_user_data(self, user, new_email):
        update_user = { 
            'id' : user.id,
            'email' : new_email,
            'first_name' : user.first_name,
            'last_name' : user.last_name,
            'user_designation' : 1,
            'permission_irf_view' : True,
            'permission_irf_add' : True,
            'permission_irf_edit' : True,
            'permission_irf_delete' : True,
            'permission_vif_view' : True,
            'permission_vif_add' : True,
            'permission_vif_edit' : True,
            'permission_vif_delete' : True,
            'permission_accounts_manage' : True,
            'permission_border_stations_view' : True,
            'permission_border_stations_add' : True,
            'permission_border_stations_edit' : True,
            'permission_vdc_manage' : True,
            'permission_budget_manage' : True,
        }
        return update_user

    def test_when_not_authenticated_should_deny_access(self):
        user = SuperUserFactory.create()
        url = reverse('Account', args=[user.id])
        new_email = 'foo@new.org'
        update_user_data = self.get_update_user_data(user, new_email)
        
        response = self.client.put(url, update_user_data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_when_authenticated_and_does_not_have_permission_should_deny_access(self):
        user = ViewUserFactory.create()
        url = reverse('Account', args=[user.id])
        self.login(user)
        new_email = 'foo@new.org'
        update_user_data = self.get_update_user_data(user, new_email)

        response = self.client.put(url, update_user_data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have the right permission to access this data') 

    def test_when_authenticated_and_has_permission_should_update_account(self):
        user = SuperUserFactory.create()
        url = reverse('Account',args=[user.id])
        self.login(user)
        new_email = 'foo@new.org'
        update_user_data = self.get_update_user_data(user, new_email)
        
        response = self.client.put(url, update_user_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], user.id)
        self.assertEqual(response.data['email'], new_email)


class AccountDeleteTests(AccountsTestCase):
    
    def test_when_not_authenticated_should_deny_access(self):
        user = SuperUserFactory.create()
        user_to_delete = ViewUserFactory.create()
        url = reverse('Account',args=[user_to_delete.id])
        
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_when_authenticated_and_does_not_have_permission_should_deny_access(self):
        user = ViewUserFactory.create()
        user_to_delete = ViewUserFactory.create()
        url = reverse('Account',args=[user_to_delete.id])
        self.login(user)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have the right permission to access this data') 

    def test_when_authenticated_and_has_permission_should_delete_account(self):
        user = SuperUserFactory.create()
        user_to_delete = ViewUserFactory.create()
        url = reverse('Account',args=[user_to_delete.id])
        self.login(user)
        
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
