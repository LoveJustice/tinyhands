from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from accounts.tests.factories import BadVifUserFactory, SuperUserFactory,ViewUserFactory, NoPermissionUserFactory
from dataentry.tests.factories import VifFactory

class RestApiTestCase(APITestCase):

    def login(self, user):
        self.client = APIClient()
        self.client.force_authenticate(user=user)


class ListVifTests(RestApiTestCase):
    def test_when_user_not_authenticated_should_deny_access(self):
        url = reverse('VictimInterview')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_when_user_authenticated_and_does_not_have_permission_should_deny_access(self):
        user = NoPermissionUserFactory.create()
        url = reverse('VictimInterview')
        self.login(user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_when_user_authenticated_has_permission_should_allow_access(self):
        user = ViewUserFactory.create()
        url = reverse('VictimInterview')
        self.login(user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetVifTests(RestApiTestCase):

    def test_when_user_not_authenticated_should_deny_access(self):
        vif_to_get = VifFactory.create()
        url = reverse('VictimInterviewDetail', args=[vif_to_get.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')
        
    def test_when_user_authenticated_and_does_not_have_permission_should_deny_access(self):
        user = NoPermissionUserFactory.create()
        vif_to_get = VifFactory.create()
        url = reverse('VictimInterviewDetail', args=[vif_to_get.id])
        self.login(user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_when_user_authenticated_and_has_permission_should_allow_access(self):
        user = ViewUserFactory.create()
        vif_to_get = VifFactory.create()
        url = reverse('VictimInterviewDetail', args=[vif_to_get.id])
        self.login(user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UpdateVifTests(RestApiTestCase):

    def get_updated_vif(self, vif, new_name):
        return {
            "id": vif.id,
            "vif_number": vif.vif_number,
            "interviewer": new_name,
            "number_of_victims": vif.number_of_victims,
            "number_of_traffickers": vif.number_of_traffickers,
            "date": vif.date,
            "date_time_entered_into_system": vif.date_time_entered_into_system,
            "date_time_last_updated": vif.date_time_last_updated,
        }

    def test_when_user_not_authenticated_should_deny_access(self):
        vif_to_put = VifFactory.create()
        url = reverse('VictimInterviewDetail', args=[vif_to_put.id])

        response = self.client.put(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_when_user_authenticated_and_does_not_have_permission_should_deny_access(self):
        user = NoPermissionUserFactory.create()
        vif_to_put = VifFactory.create()
        url = reverse('VictimInterviewDetail', args=[vif_to_put.id])
        self.login(user)
        
        new_irf = self.get_updated_vif(vif_to_put, "Fred")
        
        response = self.client.put(url, new_irf)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have the right permission to access this data')

    def test_when_user_authenticated_and_has_permission_and_vif_does_not_exist_should_return_error(self):
        user = SuperUserFactory.create()
        vif_to_put = VifFactory.create()
        url = reverse('VictimInterviewDetail', args=[2342534])
        self.login(user)

        new_irf = self.get_updated_vif(vif_to_put, "Fred")

        response = self.client.put(url, new_irf)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Not found.')

    def test_when_user_authenticated_and_has_permission_should_update_vif(self):
        user = SuperUserFactory.create()
        vif_to_put = VifFactory.create()
        url = reverse('VictimInterviewDetail', args=[vif_to_put.id])
        self.login(user)

        new_irf = self.get_updated_vif(vif_to_put, "Fred")

        response = self.client.put(url, new_irf)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

class DeleteVifTests(RestApiTestCase):

    def test_when_user_not_authenticated_should_deny_access(self):
        vif_to_delete = VifFactory.create()
        url = reverse('VictimInterviewDetail', args=[vif_to_delete.id])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_when_user_authenticated_and_does_not_have_permission_should_deny_access(self):
        user = ViewUserFactory.create()
        vif_to_delete = VifFactory.create()
        url = reverse('VictimInterviewDetail', args=[vif_to_delete.id])
        self.login(user)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have the right permission to access this data')

    def test_when_user_authenticated_and_has_permission_should_delete_vif(self):
        user = SuperUserFactory.create()
        vif_to_delete = VifFactory.create()
        url = reverse('VictimInterviewDetail', args=[vif_to_delete.id])
        self.login(user)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)