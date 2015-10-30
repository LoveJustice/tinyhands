from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase
from accounts.tests.factories import VdcUserFactory, BadVdcUserFactory, BadVifUserFactory, SuperUserFactory
from dataentry.tests.factories import VDCFactory, DistrictFactory, CannonicalNameFactory, VifFactory


class VifTest(APITestCase):
    def setUp(self):
        self.Vif_list = VifFactory.create_batch(20)
        self.user = SuperUserFactory.create()
        self.client.force_authenticate(user=self.user)

    def test_list_vif(self):
        url = reverse('VictimInterview')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 20)  # 20 is coming from the 20 VDCs we made which each have their own District

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