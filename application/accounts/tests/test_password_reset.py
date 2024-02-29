from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.tests.factories import ViewUserFactory


class AccountPasswordReset(APITestCase):
    def test_password_reset(self):
        url = reverse('PasswordReset')
        account = ViewUserFactory.create()
        old_activation_key = account.activation_key
        data = {"email": account.email}
        response = self.client.post(url, data)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(old_activation_key, account.activation_key)  # sending a password reset generates a new activation key
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset__email_not_in_database(self):
        url = reverse('PasswordReset')
        data = {"email": "test_asdf@example.com"}
        response = self.client.post(url, data)

        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_password_reset__email_not_in_request(self):
        url = reverse('PasswordReset')
        data = {}
        response = self.client.post(url, data)

        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
