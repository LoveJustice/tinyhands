from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from accounts.tests.factories import BadVifUserFactory, SuperUserFactory,ViewUserFactory, NoPermissionUserFactory
from dataentry.tests.factories import VifFactory

class RestApiTestCase(APITestCase):

    def login(self, user):
        self.client = APIClient()
        self.client.force_authenticate(user=user)

class VifTest(RestApiTestCase):
    def setUp(self):
        self.Vif_list = VifFactory.create_batch(20)
        #self.user = SuperUserFactory.create()
        #self.client.force_authenticate(user=self.user)

    def test_list_vif(self):
        url = reverse('VictimInterview')
        user = SuperUserFactory.create()
        self.login(user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 20)  # 20 is coming from the 20 Address2s we made which each have their own District

    def test_vif_403_if_doesnt_have_permission(self):
            self.bad_user = BadVifUserFactory.create()
            self.client.force_authenticate(user=self.bad_user)

            # get
            url = reverse('VictimInterview')
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

            # delete
            url = reverse('VictimInterviewDetail',  args=[self.Vif_list[0].id])
            response = self.client.delete(url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            
            
class VifTestDestroy(RestApiTestCase):     
    def test_when_not_authenticated_should_deny_access(self):
        
        vif_to_delete = VifFactory.create()
        url = reverse('VictimInterviewDetail',args=[vif_to_delete.id])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_when_authenticated_and_does_not_have_permission_should_deny_access(self):
        user = ViewUserFactory.create()
        vif_to_delete = VifFactory.create()
        url = reverse('VictimInterviewDetail',args=[vif_to_delete.id])
        self.login(user)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have the right permission to access this data')

    def test_when_authenticated_and_has_permission_should_delete_vif(self):
        user = SuperUserFactory.create()
        vif_to_delete = VifFactory.create()
        url = reverse('VictimInterviewDetail',args=[vif_to_delete.id])
        self.login(user)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

class VifTestGet_list(RestApiTestCase):
    def test_when_not_authenticated_should_deny_access(self):
        url = reverse('VictimInterview')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_when_authenticated_has_permission_should_allow_access(self):
        user = ViewUserFactory.create()
        url = reverse('VictimInterview')
        self.login(user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_when_authenticated_does_not_have_permission_should_deny_access(self):
        user = NoPermissionUserFactory.create()
        url = reverse('VictimInterview')
        self.login(user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class VifTestGet_Details(RestApiTestCase):     
    def test_when_not_authenticated_should_deny_access(self):
        vif_to_get = VifFactory.create()
        url = reverse('VictimInterviewDetail',args=[vif_to_get.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_when_authenticated_has_permission_should_allow_access(self):
        user = ViewUserFactory.create()
        vif_to_get = VifFactory.create()
        url = reverse('VictimInterviewDetail',args=[vif_to_get.id])
        self.login(user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_when_authenticated_does_not_have_permission_should_deny_access(self):
        user = NoPermissionUserFactory.create()
        vif_to_get = VifFactory.create()
        url = reverse('VictimInterviewDetail',args=[vif_to_get.id])
        self.login(user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
class VifTestPut(RestApiTestCase):

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
            "victim_name" : new_name,
            "victim_gender" : "M"
        }


    def test_when_not_authenticated_should_deny_access(self):
        vif_to_put = VifFactory.create()
        url = reverse('VictimInterviewDetail',args=[vif_to_put.id])

        response = self.client.put(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)     
    
    #This is not working needs more tests
    def test_when_authenticated_and_does_not_have_permission_should_allow_access(self):
        user = SuperUserFactory.create()         
        vif_to_put = VifFactory.create()
        url = reverse('VictimInterviewDetail',args=[vif_to_put.id])
        self.login(user)
        
        new_irf = self.get_updated_vif(vif_to_put, "Fred")
        
        response = self.client.put(url, new_irf)

        self.assertEqual(response.data, status.HTTP_403_FORBIDDEN)
