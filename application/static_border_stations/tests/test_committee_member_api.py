import json
from django.core.urlresolvers import reverse
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
        border_station = self.committee_member.border_station
        self.committee_member.member_projects.add(border_station)
        self.other_committee_members = CommitteeMemberFactory.create_batch(4)
        for member in self.other_committee_members:
            member.member_projects.add(border_station)
        

    # Authentication Methods

    def test_when_not_authenticated_should_deny_access(self):
        url = reverse('CommitteeMember')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertIn('Authentication credentials were not provided', response.data['detail'])

    # Viewset Methods

    def test_return_all_CommitteeMembers(self):
        usr = GenericUserWithPermissions.create([{'group':'SUBCOMMITTEE', 'action':'VIEW_BASIC', 'country': None, 'station': None},])
        self.login(usr)
        url = reverse('CommitteeMember')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)

    def test_create_CommitteeMember(self):
        usr = GenericUserWithPermissions.create([{'group':'SUBCOMMITTEE', 'action':'VIEW_BASIC', 'country': None, 'station': None},{'group':'SUBCOMMITTEE', 'action':'ADD', 'country': None, 'station': None}])
        self.login(usr)
        url = reverse('CommitteeMember')
        email = "TEST@TEST.COM"

        data = {
            "member":json.dumps({
                "email": email,
                "first_name": "asdf",
                "last_name": "asdf",
                "phone": "204-123-123",
                "position": "asdf",
                "receives_money_distribution_form": True,
                "border_station": self.committee_member.border_station_id,
            })
        }

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(email, response.data['email'])

    def test_get_CommitteeMember(self):
        usr = GenericUserWithPermissions.create([{'group':'SUBCOMMITTEE', 'action':'VIEW_BASIC', 'country': None, 'station': None},])
        self.login(usr)
        url = reverse('CommitteeMemberDetail', args=[self.committee_member.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.committee_member.email, response.data['email'])

    def test_update_CommitteeMember(self):
        usr = GenericUserWithPermissions.create([{'group':'SUBCOMMITTEE', 'action':'VIEW_BASIC', 'country': None, 'station': None},{'group':'SUBCOMMITTEE', 'action':'EDIT_BASIC', 'country': None, 'station': None}])
        self.login(usr)
        url = reverse('CommitteeMemberDetail', args=[self.committee_member.id])
        email = "TEST@TEST.COM"

        data = {
            "member":json.dumps({
                "email": email,
                "first_name": "asdf",
                "last_name": "asdf",
                "phone": "204-123-123",
                "position": "asdf",
                "receives_money_distribution_form": True,
                "border_station": self.committee_member.border_station_id,
            })
        }

        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(email, response.data['email'])

    def test_delete_CommitteeMember(self):
        usr = GenericUserWithPermissions.create([{'group':'SUBCOMMITTEE', 'action':'VIEW_BASIC', 'country': None, 'station': None},{'group':'SUBCOMMITTEE', 'action':'DELETE', 'country': None, 'station': None}])
        self.login(usr)
        url = reverse('CommitteeMemberDetail', args=[self.committee_member.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_CommitteeMember_by_border_station(self):
        for mem in self.other_committee_members:
            mem.border_station = self.committee_member.border_station
            mem.save()

        usr = GenericUserWithPermissions.create([{'group':'SUBCOMMITTEE', 'action':'VIEW_BASIC', 'country': None, 'station': None},])
        self.login(usr)
        url = reverse('CommitteeMember') + "?project_id=" + str(self.committee_member.border_station_id)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 5)
