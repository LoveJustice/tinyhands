from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase
from dataentry.models import Person
from dataentry.models import VictimInterview
from accounts.tests.factories import SuperUserFactory
from dataentry.tests.factories import PersonFactory, VifFactory, IrfFactory, IntercepteeNoPhotoFactory, PersonBoxFactory, AliasGroupFactory

class IDManagementTest(APITestCase):
    def setUp(self):
        self.phone_match = '9876543210'
        self.person_list = PersonFactory.create_batch(11)
        self.user = SuperUserFactory.create()
        self.client.force_authenticate(user=self.user)
        self.interceptee_list = IntercepteeNoPhotoFactory.create_batch(3)
        self.pb_list = PersonBoxFactory.create_batch(2)
        self.irf_list = IrfFactory.create_batch(2)
        self.vif_list = VifFactory.create_batch(2)
        self.alias_list = AliasGroupFactory.create_batch(1)

        self.interceptee_list[0].person = self.person_list[0]
        self.pb_list[0].person = self.person_list[0]
        self.pb_list[1].person = self.person_list[0]
        self.interceptee_list[1].person = self.person_list[1]
        self.vif_list[0].victim = self.person_list[2]
        self.interceptee_list[2].person = self.person_list[3]
        self.vif_list[1].victim = self.person_list[4]

        self.person_list[3].alias_group = self.alias_list[0]
        self.person_list[4].alias_group = self.alias_list[0]

        self.person_list[3].phone_contact = self.phone_match + '01'
        self.person_list[4].phone_contact = self.phone_match + '02'

        self.person_list[3].full_name = "Raymond Smith"
        self.person_list[4].full_name = "Raymond Smythe"

        self.interceptee_list[0].interception_record = self.irf_list[0]
        self.interceptee_list[1].interception_record = self.irf_list[1]
        self.interceptee_list[2].interception_record = self.irf_list[1]

        self.pb_list[0].victim_interview = self.vif_list[0]
        self.pb_list[1].victim_interview = self.vif_list[1]

        for idx in range(0,3):
            self.interceptee_list[idx].save()

        for idx in range(0,2):
            self.pb_list[idx].save()

        for idx in range(0,2):
            self.vif_list[idx].save()

        for idx in range(0,5):
            self.person_list[idx].save()

    def test_list_persons(self):
        url = reverse('IDManagement')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 20)

    def test_fuzzy_search(self):
        url = reverse('IDManagementFuzzy')
        data = {'name': self.person_list[3].full_name}

        response = self.client.get(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_phone_search(self):
        url = reverse('IDManagementPhone')
        data = {'phone': self.phone_match}

        response = self.client.get(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_person_forms(self):
        url = reverse('IDManagementForms')
        data = {'person_id': self.person_list[0].id}

        response = self.client.get(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        cmpForm = []
        for idx in range(0, len(response.data)):
            cmpForm.append(response.data[idx]['number'])

        self.assertTrue(self.irf_list[0].irf_number in cmpForm, "missing irf")
        self.assertTrue(self.vif_list[0].vif_number in cmpForm, "missing vif1")
        self.assertTrue(self.vif_list[1].vif_number in cmpForm, "missing vif2")

    def test_add_alias(self):
        url = reverse('IDManagementAdd', args=[self.person_list[1].id, self.person_list[2].id])

        response = self.client.put(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        person1 = Person.objects.get(id=self.person_list[1].id)
        person2 = Person.objects.get(id=self.person_list[2].id)
        self.assertFalse(person1.alias_group is None, "person1 alias group is None")
        self.assertFalse(person2.alias_group is None, "person2 alias group is None")
        self.assertEqual(person1.alias_group.id, person2.alias_group.id)

    def test_alias_members(self):
        url = reverse('IDManagementGroup')
        data = {'group_id': self.alias_list[0].id}

        response = self.client.get(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_remove_alias(self):
        url = reverse('IDManagementRemove', args=[self.person_list[3].id])

        response = self.client.put(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        person1 = Person.objects.get(id=self.person_list[3].id)
        person2 = Person.objects.get(id=self.person_list[4].id)
        self.assertTrue(person1.alias_group is None, "person1 alias group is not None")
        self.assertTrue(person2.alias_group is None, "person2 alias group is not None")
