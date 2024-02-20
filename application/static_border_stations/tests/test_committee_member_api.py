from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from static_border_stations.tests.factories import *


class RestApiTestCase(APITestCase):
    def login(self, user):
        self.client = APIClient()
        self.client.force_authenticate(user=user)


class CommitteeMemberTests(RestApiTestCase):
    fixtures = ['initial-required-data/Region.json','initial-required-data/Country.json', 'initial-required-data/Permission.json']
    def setUp(self):
        self.committee_member = CommitteeMemberFactory.create()
        self.committee_member.save()
        self.other_committee_members = CommitteeMemberFactory.create_batch(4)

    # Authentication Methods

    def test_when_not_authenticated_should_deny_access(self):
        url = reverse('CommitteeMember')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertIn('Authentication credentials were not provided', response.data['detail'])

    # Viewset Methods

    def test_return_all_CommitteeMembers(self):
        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None},])
        self.login(usr)
        url = reverse('CommitteeMember')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)

    def test_create_CommitteeMember(self):
        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None},{'group':'PROJECTS', 'action':'ADD', 'country': None, 'station': None}])
        self.login(usr)
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
        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None},])
        self.login(usr)
        url = reverse('CommitteeMemberDetail', args=[self.committee_member.id])
        self.committee_member.save()
        print("=====", self.committee_member.id)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.committee_member.email, response.data['email'])

    def test_update_CommitteeMember(self):
        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None},{'group':'PROJECTS', 'action':'EDIT', 'country': None, 'station': None}])
        self.login(usr)
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
        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None},{'group':'PROJECTS', 'action':'EDIT', 'country': None, 'station': None}])
        self.login(usr)
        url = reverse('CommitteeMemberDetail', args=[self.committee_member.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_CommitteeMember_by_border_station(self):
        for mem in self.other_committee_members:
            mem.border_station = self.committee_member.border_station
            mem.save()

        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None},])
        self.login(usr)
        url = reverse('CommitteeMember') + "?border_station=" + str(self.committee_member.border_station_id)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 5)
