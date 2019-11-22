from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.tests.factories import BadIrfUserFactory, SuperUserFactory
from dataentry.tests.factories import IntercepteeFactory
from dataentry.models import Permission, UserLocationPermission


class PhotoTest(APITestCase):
    fixtures = ['initial-required-data/Country.json', 'initial-required-data/Permission.json']
    def setUp(self):
        IntercepteeFactory.create_batch(20)
        self.user = SuperUserFactory.create()
        self.client.force_authenticate(user=self.user)
        ulp = UserLocationPermission()
        ulp.account = self.user
        ulp.permission = Permission.objects.get(permission_group='FORMS', action='CLASSIC')
        ulp.save()

    def test_photo_count_contains_all_photos(self):
        url = reverse('PhotoExporterCount', kwargs={"start_date": "8-4-2007", "end_date": "8-4-2013"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 20)

    def test_photo_count_contains_zero_photos(self):
        url = reverse('PhotoExporterCount', kwargs={"start_date": "8-4-2014", "end_date": "8-4-2015"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_irf_403_if_doesnt_have_permission(self):
        self.bad_user = BadIrfUserFactory.create()
        self.client.force_authenticate(user=self.bad_user)

        # get
        url = reverse('PhotoExporter', kwargs={"start_date": "8-4-2007", "end_date": "8-4-2013"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # get
        url = reverse('PhotoExporterCount', kwargs={"start_date": "8-4-2007", "end_date": "8-4-2013"})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # With Unauthenticated User
        self.bad_user = BadIrfUserFactory.create()
        self.client.force_authenticate(user=None)

        url = reverse('PhotoExporter', kwargs={"start_date": "8-4-2007", "end_date": "8-4-2013"})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        url = reverse('PhotoExporterCount', kwargs={"start_date": "8-4-2007", "end_date": "8-4-2013"})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
