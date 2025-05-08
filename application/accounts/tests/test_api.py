from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from accounts.tests.factories import SuperUserFactory, ViewUserFactory, SuperUserDesignation, ViewUserDesignation


class RestApiTestCase(APITestCase):
    def login(self, user):
        self.client = APIClient()
        self.client.force_authenticate(user=user)


class AccountsGetTests(RestApiTestCase):
    def test_when_not_authenticated_should_deny_access(self):
        url = reverse('AccountList')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_when_authenticated_and_does_not_have_permission_should_deny_access(self):
        url = reverse('AccountList')
        user = ViewUserFactory.create()
        self.login(user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have the right permission to access this data')

    def test_when_authenticated_and_has_permission_should_return_all_accounts(self):
        url = reverse('AccountList')
        user = SuperUserFactory.create()
        self.login(user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class AccountsPostTests(RestApiTestCase):
    email = 'foo@bar.org'
    first_name = 'Test'
    last_name = 'Tester'

    def get_user_data(self, user):
        return {
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'user_designation': user.user_designation.id,
            'permission_irf_view': True,
            'permission_irf_add': True,
            'permission_irf_edit': True,
            'permission_irf_delete': True,
            'permission_vif_view': True,
            'permission_vif_add': True,
            'permission_vif_edit': True,
            'permission_vif_delete': True,
            'permission_person_match': True,
            'permission_accounts_manage': True,
            'permission_border_stations_view': True,
            'permission_border_stations_add': True,
            'permission_border_stations_edit': True,
            'permission_vdc_manage': True,
            'permission_budget_view': True,
            'permission_budget_add': True,
            'permission_budget_edit':  True,
            'permission_budget_delete': True,
        }

    def test_when_not_authenticated_should_deny_access(self):
        url = reverse('AccountList')

        response = self.client.post(url, {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_when_authenticated_and_does_not_have_permission_should_deny_access(self):
        url = reverse('AccountList')
        user = ViewUserFactory.create()
        self.login(user)

        response = self.client.post(url, self.get_user_data(user))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have the right permission to access this data')

    def test_when_authenticated_and_has_permission_should_create_account(self):
        url = reverse('AccountList')
        user = SuperUserFactory.create()
        self.login(user)

        response = self.client.post(url, self.get_user_data(user))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], self.email)
        self.assertEqual(response.data['first_name'], self.first_name)
        self.assertEqual(response.data['last_name'], self.last_name)


class AccountGetTests(RestApiTestCase):

    def test_when_not_authenticated_should_deny_access(self):
        user = SuperUserFactory.create()
        url = reverse('Account', args=[user.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
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
        url = reverse('Account', args=[user.id])
        self.login(user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], user.id)
        self.assertEqual(response.data['email'], user.email)


class AccountPutTests(RestApiTestCase):
    def get_update_user_data(self, user, new_email):
        update_user = {
            'id': user.id,
            'email': new_email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'user_designation': user.user_designation.id,
            'permission_irf_view': True,
            'permission_irf_add': True,
            'permission_irf_edit': True,
            'permission_irf_delete': True,
            'permission_vif_view': True,
            'permission_vif_add': True,
            'permission_vif_edit': True,
            'permission_vif_delete': True,
            'permission_person_match': True,
            'permission_accounts_manage': True,
            'permission_border_stations_view': True,
            'permission_border_stations_add': True,
            'permission_border_stations_edit': True,
            'permission_address2_manage': True,
            'permission_budget_view': True,
            'permission_budget_add': True,
            'permission_budget_edit':  True,
            'permission_budget_delete': True,
        }
        return update_user

    def test_when_not_authenticated_should_deny_access(self):
        user = SuperUserFactory.create()
        url = reverse('Account', args=[user.id])
        new_email = 'foo@new.org'
        update_user_data = self.get_update_user_data(user, new_email)

        response = self.client.put(url, update_user_data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
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
        url = reverse('Account', args=[user.id])
        self.login(user)
        new_email = 'foo@new.org'
        update_user_data = self.get_update_user_data(user, new_email)

        response = self.client.put(url, update_user_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], user.id)
        self.assertEqual(response.data['email'], new_email)


class AccountDeleteTests(RestApiTestCase):

    def test_when_not_authenticated_should_deny_access(self):
        user_to_delete = ViewUserFactory.create()
        url = reverse('Account', args=[user_to_delete.id])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_when_authenticated_and_does_not_have_permission_should_deny_access(self):
        user = ViewUserFactory.create()
        user_to_delete = ViewUserFactory.create()
        url = reverse('Account', args=[user_to_delete.id])
        self.login(user)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have the right permission to access this data')

    def test_when_authenticated_and_has_permission_should_delete_account(self):
        user = SuperUserFactory.create()
        user_to_delete = ViewUserFactory.create()
        url = reverse('Account', args=[user_to_delete.id])
        self.login(user)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class DefaultPermissionsSetsGetTests(RestApiTestCase):

    def test_when_not_authenticated_should_deny_access(self):
        url = reverse('DefaultPermissionsSets')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_when_authenticated_and_does_not_have_permission_should_deny_access(self):
        url = reverse('DefaultPermissionsSets')
        user = ViewUserFactory.create()
        self.login(user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have the right permission to access this data')

    def test_when_authenticated_and_has_permission_should_return_all_default_permissions_sets(self):
        url = reverse('DefaultPermissionsSets')
        user = SuperUserFactory.create()
        self.login(user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class DefaultPermissionsSetsPostTests(RestApiTestCase):

    name = 'new_set'
    new_permission_set = {
        'name': name,
        'permission_irf_view': True,
        'permission_irf_add': True,
        'permission_irf_edit': True,
        'permission_irf_delete': True,
        'permission_vif_view': True,
        'permission_vif_add': True,
        'permission_vif_edit': True,
        'permission_vif_delete': True,
        'permission_person_match': True,
        'permission_accounts_manage': True,
        'permission_border_stations_view': True,
        'permission_border_stations_add': True,
        'permission_border_stations_edit': True,
        'permission_address2_manage': True,
        'permission_budget_view': True,
        'permission_budget_add': True,
        'permission_budget_edit':  True,
        'permission_budget_delete': True,
    }

    def test_when_not_authenticated_should_deny_access(self):
        url = reverse('DefaultPermissionsSets')

        response = self.client.post(url, self.new_permission_set)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_when_authenticated_and_does_not_have_permission_should_deny_access(self):
        url = reverse('DefaultPermissionsSets')
        user = ViewUserFactory.create()
        self.login(user)

        response = self.client.post(url, self.new_permission_set)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have the right permission to access this data')

    def test_when_authenticated_and_has_permission_should_create_new_default_permissions_sets(self):
        url = reverse('DefaultPermissionsSets')
        user = SuperUserFactory.create()
        self.login(user)

        response = self.client.post(url, self.new_permission_set)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], self.name)


class DefaultPermissionsSetGetTests(RestApiTestCase):

    def test_when_not_authenticated_should_deny_access(self):
        name = 'set_to_get'
        permission_set = SuperUserDesignation.create(name=name)
        url = reverse('DefaultPermissionsSet', args=[permission_set.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_when_authenticated_and_does_not_have_permission_should_deny_access(self):
        name = 'set_to_get'
        permission_set = SuperUserDesignation.create(name=name)
        url = reverse('DefaultPermissionsSet', args=[permission_set.id])
        user = ViewUserFactory.create()
        self.login(user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have the right permission to access this data')

    def test_when_authenticated_and_has_permission_should_return_default_permissions_set(self):
        name = 'set_to_get'
        permission_set = SuperUserDesignation.create(name=name)
        url = reverse('DefaultPermissionsSet', args=[permission_set.id])
        user = SuperUserFactory.create()
        self.login(user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], name)


class DefaultPermissionsSetPutTests(RestApiTestCase):

    def get_update_permission_set(self, permission_set, new_name):
        update_permission_set = {
            'id': permission_set.id,
            'name': new_name,
            'permission_irf_view': True,
            'permission_irf_add': True,
            'permission_irf_edit': True,
            'permission_irf_delete': True,
            'permission_vif_view': True,
            'permission_vif_add': True,
            'permission_vif_edit': True,
            'permission_vif_delete': True,
            'permission_person_match': True,
            'permission_accounts_manage': True,
            'permission_border_stations_view': True,
            'permission_border_stations_add': True,
            'permission_border_stations_edit': True,
            'permission_address2_manage': True,
            'permission_budget_view': True,
            'permission_budget_add': True,
            'permission_budget_edit':  True,
            'permission_budget_delete': True,
        }
        return update_permission_set

    def test_when_not_authenticated_should_deny_access(self):
        name = 'set_to_get'
        permission_set = SuperUserDesignation.create(name=name)
        url = reverse('DefaultPermissionsSet', args=[permission_set.id])
        new_name = 'new_name_for_set'
        update_permission_set = self.get_update_permission_set(permission_set, new_name)

        response = self.client.put(url, update_permission_set)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_when_authenticated_and_does_not_have_permission_should_deny_access(self):
        name = 'set_to_get'
        permission_set = SuperUserDesignation.create(name=name)
        url = reverse('DefaultPermissionsSet', args=[permission_set.id])

        user = ViewUserFactory.create()
        self.login(user)

        new_name = 'new_name_for_set'
        update_permission_set = self.get_update_permission_set(permission_set, new_name)

        response = self.client.put(url, update_permission_set)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have the right permission to access this data')

    def test_when_authenticated_and_has_permission_should_return_updated_permissions_set(self):
        name = 'set_to_get'
        permission_set = SuperUserDesignation.create(name=name)
        url = reverse('DefaultPermissionsSet', args=[permission_set.id])
        user = SuperUserFactory.create()
        self.login(user)

        new_name = 'new_name_for_set'
        update_permission_set = self.get_update_permission_set(permission_set, new_name)

        response = self.client.put(url, update_permission_set)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], new_name)


class DefaultPermissionsSetDeleteTests(RestApiTestCase):

    def test_when_not_authenticated_should_deny_access(self):
        permission_set = SuperUserDesignation.create()
        url = reverse('DefaultPermissionsSet', args=[permission_set.id])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_when_authenticated_and_does_not_have_permission_should_deny_access(self):
        permission_set = SuperUserDesignation.create()
        url = reverse('DefaultPermissionsSet', args=[permission_set.id])
        user = ViewUserFactory.create()
        self.login(user)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have the right permission to access this data')

    def test_when_authenticated_and_has_permission_and_permissions_set_used_by_accounts_should_not_delete_default_permissions_set(self):
        permission_set = SuperUserDesignation.create()
        url = reverse('DefaultPermissionsSet', args=[permission_set.id])
        user = SuperUserFactory.create()
        self.login(user)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Permission set is currently used by accounts. It cannot be deleted.')

    def test_when_authenticated_and_has_permission_and_permissions_set_not_used_by_accounts_should_delete_default_permissions_set(self):
        permission_set = ViewUserDesignation.create()
        url = reverse('DefaultPermissionsSet', args=[permission_set.id])
        user = SuperUserFactory.create()
        self.login(user)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CurrentUserTests(RestApiTestCase):

    def test_when_not_logged_in_should_deny_access(self):
        url = reverse('CurrentUser')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_when_logged_in_should_return_logged_in_users_account(self):
        user = SuperUserFactory.create()
        self.login(user)
        url = reverse('CurrentUser')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], user.id)
        self.assertEqual(response.data['email'], user.email)

