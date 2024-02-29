from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase
from accounts.tests.factories import Address2UserFactory, BadAddress2UserFactory
from dataentry.models import Address2
from dataentry.models import Person
from dataentry.models import VictimInterview
from dataentry.models import VictimInterviewLocationBox
from dataentry.tests.factories import Address2Factory, Address1Factory, CanonicalNameFactory, PersonFactory, VifFactory, VictimInterviewLocationBoxFactory


class Address1RelatedItemsTest(APITestCase):
    def setUp(self):
        self.address1_list = Address1Factory.create_batch(20)
        self.user = Address2UserFactory.create()
        self.client.force_authenticate(user=self.user)
        self.data = {
            'name': 'Address1',
            "completed": False,
        }

    def test_retrieve_related_items(self):
        address2 = Address2Factory.create()
        address1 = address2.address1
        person = PersonFactory.create(address1=address1)
        vif = VifFactory.create(victim_guardian_address1=address1)

        mapperD = {'person': person, 'victiminterview': vif, 'address2': address2 }

        url = reverse('Address1RelatedItems', args=[address1.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], address1.id)

        related_items = response.data['related_items']
        for item in related_items:
            if item['type'] in mapperD:
                self.assertEqual(True, mapperD[item['type']].id in [obj['id'] for obj in item['objects']])
        self.assertEqual(response.data['id'], address1.id)

    def test_remove_address1_with_related_items__should_not_work(self):
        address2 = Address2Factory.create()
        address1 = address2.address1
        person = PersonFactory.create(address1=address1)
        vif = VifFactory.create(victim_guardian_address1=address1)
        url = reverse('Address1detail', args=[address1.id])

        for related_object in [address2, person, vif]:
            response = self.client.delete(url)
            self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
            related_object.delete()

        # All related objects are deleted now, so the Address should be able to be deleted now
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_address_related_items_swap(self):
        address2 = Address2Factory.create()
        address1 = address2.address1
        new_address1 = Address1Factory.create()
        person = PersonFactory.create(address1=address1)
        vif = VifFactory.create(victim_guardian_address1=address1)
        viflb = VictimInterviewLocationBoxFactory.create(address1=address1)

        url = reverse('Address1RelatedItemsSwap', args=[address1.id, new_address1.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Address2.objects.filter(address1=address1).count(), 0)
        self.assertEqual(Person.objects.filter(address1=address1).count(), 0)
        self.assertEqual(VictimInterview.objects.filter(victim_guardian_address1=address1).count(), 0)
        self.assertEqual(VictimInterviewLocationBox.objects.filter(address1=address1).count(), 0)

        self.assertEqual(Person.objects.filter(address1=new_address1).count(), 1)
        self.assertEqual(Address2.objects.filter(address1=new_address1).count(), 1)
        self.assertEqual(VictimInterview.objects.filter(victim_guardian_address1=new_address1).count(), 1)
        self.assertEqual(VictimInterviewLocationBox.objects.filter(address1=new_address1).count(), 1)


class Address2RelatedItemsTest(APITestCase):

    def setUp(self):
        self.user = Address2UserFactory.create()
        self.client.force_authenticate(user=self.user)

        self.Address2List = Address2Factory.create_batch(20)
        self.factory = APIRequestFactory()
        self.first_address1 = self.Address2List[0].address1
        self.first_canonical_name = self.Address2List[0].canonical_name
        self.data = {
            'name': 'Address2',
            "verified": False,
            "address1": {
                "id": self.first_address1.id,
                "name": self.first_address1.name,
            },
            "canonical_name": {
                "id": self.first_canonical_name.id,
                "name": self.first_canonical_name.name,
            },
        }

    def test_retrieve_related_items_address2(self):
        address2 = Address2Factory.create()

        related_address2 = Address2Factory.create(canonical_name=address2)
        person = PersonFactory.create(address2=address2)
        vif = VifFactory.create(victim_guardian_address2=address2)

        mapperD = {'person': person, 'victiminterview': vif, 'address2': related_address2 }

        url = reverse('Address2RelatedItems', args=[address2.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], address2.id)

        related_items = response.data['related_items']
        for item in related_items:
            if item['type'] in mapperD:
                self.assertEqual(True, mapperD[item['type']].id in [obj['id'] for obj in item['objects']])
        self.assertEqual(response.data['id'], address2.id)

    def test_remove_address2_with_related_items__should_not_work(self):
        address2 = Address2Factory.create()
        related_address2 = Address2Factory.create(canonical_name=address2)
        person = PersonFactory.create(address2=address2)
        vif = VifFactory.create(victim_guardian_address2=address2)
        url = reverse('Address2detail', args=[address2.id])

        for related_object in [related_address2, person, vif]:
            response = self.client.delete(url)
            self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
            related_object.delete()

        # All related objects are deleted now, so the Address should be able to be deleted now
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_address_related_items_swap(self):
        address2 = Address2Factory.create(canonical_name=Address2Factory.create())
        related_address2 = Address2Factory.create()
        related_address2.canonical_name = address2
        related_address2.save()

        new_address2 = Address2Factory.create()
        person = PersonFactory.create(address2=address2)
        vif = VifFactory.create(victim_guardian_address2=address2)
        viflb = VictimInterviewLocationBoxFactory.create(address2=address2)

        url = reverse('Address2RelatedItemsSwap', args=[address2.id, new_address2.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Address2.objects.filter(address2=address2).count(), 0)
        self.assertEqual(VictimInterview.objects.filter(victim_guardian_address2=address2).count(), 0)
        self.assertEqual(VictimInterviewLocationBox.objects.filter(address2=address2).count(), 0)
        self.assertEqual(Person.objects.filter(address2=address2).count(), 0)

        self.assertEqual(Person.objects.filter(address2=new_address2).count(), 1)
        self.assertEqual(Address2.objects.filter(address2=new_address2).count(), 1)
        self.assertEqual(VictimInterview.objects.filter(victim_guardian_address2=new_address2).count(), 1)
        self.assertEqual(VictimInterviewLocationBox.objects.filter(address2=new_address2).count(), 1)

    def test_address_related_items_swap(self):
        address2 = Address2Factory.create(canonical_name=Address2Factory.create())
        related_address2 = Address2Factory.create()
        related_address2.canonical_name = address2
        related_address2.save()

        person = PersonFactory.create(address2=address2)
        vif = VifFactory.create(victim_guardian_address2=address2)
        viflb = VictimInterviewLocationBoxFactory.create(address2=address2)

        url = reverse('Address2RelatedItemsSwap', args=[address2.id, related_address2.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)




