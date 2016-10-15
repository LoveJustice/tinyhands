from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from accounts.tests.factories import NoPermissionUserFactory, SuperUserFactory


class IrfCsvExportView(APITestCase):

    def test_when_user_not_authenticated_should_return_404(self):
        url = reverse('InterceptionRecordCsvExport')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_when_user_is_authenticated_and_does_not_have_permission_should_return_403(self):
        url = reverse('InterceptionRecordCsvExport')
        self.client.force_authenticate(user=NoPermissionUserFactory.create())

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have the right permission to access this data')

    def test_when_user_is_authenticated_and_does_have_permission_should_return_csv_file(self):
        url = reverse('InterceptionRecordCsvExport')
        self.client.force_authenticate(user=SuperUserFactory.create())

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class VifCsvExportView(APITestCase):

    def test_when_user_not_authenticated_should_return_404(self):
        url = reverse('VictimInterviewCsvExport')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_when_user_is_authenticated_and_does_not_have_permission_should_return_403(self):
        url = reverse('VictimInterviewCsvExport')
        self.client.force_authenticate(user=NoPermissionUserFactory.create())

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have the right permission to access this data')

    def test_when_user_is_authenticated_and_does_have_permission_should_return_csv_file(self):
        url = reverse('VictimInterviewCsvExport')
        self.client.force_authenticate(user=SuperUserFactory.create())

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)