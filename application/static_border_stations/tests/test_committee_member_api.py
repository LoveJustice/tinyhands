from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from static_border_stations.tests.factories import *


class RestApiTestCase(APITestCase):
    def login(self, user):
        self.client = APIClient()
        self.client.force_authenticate(user=user)


class CommitteeMemberTests(RestApiTestCase):
    def setUp(self):
        self.committee_member = CommitteeMemberFactory.create()
        self.other_committee_members = CommitteeMemberFactory.create_batch(4)

    # Authentication Methods

    def test_when_not_authenticated_should_deny_access(self):
        url = reverse('CommitteeMember')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertIn('Authentication credentials were not provided', response.data['detail'])

    def test_when_authenticated_and_does_not_have_permission_should_deny_access(self):
        self.login(UnauthorizedBorderStationUser.create())
        url = reverse('CommitteeMember')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Viewset Methods

    def test_return_all_CommitteeMembers(self):
        self.login(ViewBorderStationUser.create())
        url = reverse('CommitteeMember')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)

    def test_create_CommitteeMember(self):
        self.login(AddBorderStationUser.create())
        url = reverse('CommitteeMember')

        data = {
            "email": "TEST@TEST.COM",
            "first_name": "asdf",
            "last_name": "asdf",
            "phone": "204-123-123",
            "position": "asdf",
            "receives_money_distribution_form": True,
            "border_station": self.committee_member.border_station_id,
        }

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(data['email'], response.data['email'])

    def test_get_CommitteeMember(self):
        self.login(ViewBorderStationUser.create())
        url = reverse('CommitteeMemberDetail', args=[self.committee_member.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.committee_member.email, response.data['email'])

    def test_update_CommitteeMember(self):
        self.login(EditBorderStationUser.create())
        url = reverse('CommitteeMemberDetail', args=[self.committee_member.id])

        data = {
            "email": "TEST@TEST.COM",
            "first_name": "asdf",
            "last_name": "asdf",
            "phone": "204-123-123",
            "position": "asdf",
            "receives_money_distribution_form": True,
            "border_station": self.committee_member.border_station_id,
        }

        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['email'], response.data['email'])

    def test_delete_CommitteeMember(self):
        self.login(DeleteBorderStationUser.create())
        url = reverse('CommitteeMemberDetail', args=[self.committee_member.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_CommitteeMember_by_border_station(self):
        for mem in self.other_committee_members:
            mem.border_station = self.committee_member.border_station
            mem.save()

        self.login(DeleteBorderStationUser.create())
        url = reverse('CommitteeMember') + "?border_station=" + str(self.committee_member.border_station_id)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 5)
