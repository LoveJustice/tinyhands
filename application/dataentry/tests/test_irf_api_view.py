from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.tests.factories import BadIrfUserFactory, SuperUserFactory
from dataentry.tests.factories import IrfFactory


class IrfTest(APITestCase):
    def setUp(self):
        self.irf_list = IrfFactory.create_batch(20)
        self.user = SuperUserFactory.create()
        self.client.force_authenticate(user=self.user)

    def test_list_irfs(self):
        url = reverse('InterceptionRecord')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 20)  # 20 is coming from the 20 Address2s we made which each have their own Address1

    def test_irf_403_if_doesnt_have_permission(self):
        self.bad_user = BadIrfUserFactory.create()
        self.client.force_authenticate(user=self.bad_user)

        # get
        url = reverse('InterceptionRecord')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # delete
        url = reverse('InterceptionRecordDetail', args=[self.irf_list[0].id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
