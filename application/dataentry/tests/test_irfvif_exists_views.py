from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.tests.factories import BadIrfUserFactory, SuperUserFactory
from dataentry.tests.factories import IrfFactory, VifFactory


class IrfExistsTest(APITestCase):
    def setUp(self):
        self.irf_list = IrfFactory.create_batch(20)
        self.user = SuperUserFactory.create()
        self.client.force_authenticate(user=self.user)

    def test_irfexists_returns_irf_number_if_exists(self):
        irf_number = self.irf_list[0].irf_number
        url = reverse('IrfExists', args=[irf_number])

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, irf_number)

    def test_irfexists_allows_optional_letters_after_the_number(self):
        irf_number = "BHD123BA"
        irf = IrfFactory.create(irf_number="BHD123BA")
        url = reverse('IrfExists', args=[irf_number])

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, irf_number)

    def test_irfexists_returns_error_if_doesnt_exist(self):
        url = reverse('IrfExists', args=["BHD123ASDASD"])

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, "Irf does not exist")


class VifExistsTest(APITestCase):
    def setUp(self):
        self.vif_list = VifFactory.create_batch(20)
        self.user = SuperUserFactory.create()
        self.client.force_authenticate(user=self.user)

    def test_vifexists_returns_vif_number_if_exists(self):
        vif_number = self.vif_list[0].vif_number
        url = reverse('VifExists', args=[vif_number])

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, vif_number)

    def test_vifexists_allows_optional_letters_after_the_number(self):
        vif_number = "BHD123BA"
        vif = VifFactory.create(vif_number="BHD123BA")
        url = reverse('VifExists', args=[vif_number])

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, vif_number)

    def test_vifexists_returns_error_if_doesnt_exist(self):
        url = reverse('VifExists', args=["BHD123ASDASD"])

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, "Vif does not exist")

