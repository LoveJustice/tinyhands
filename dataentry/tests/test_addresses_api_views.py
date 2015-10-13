from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase
from accounts.tests.factories import VdcUserFactory, BadVdcUserFactory
from dataentry.tests.factories import VDCFactory, DistrictFactory, CannonicalNameFactory


class Address1Test(APITestCase):
    def setUp(self):
        self.district_list = DistrictFactory.create_batch(20)
        self.user = VdcUserFactory.create()
        self.client.force_authenticate(user=self.user)

    def test_create_address1(self):

        url = reverse('Address1')
        data = {'name': 'Address1'}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Address1')
        self.assertIsNotNone(response.data['id'])

    def test_list_address1s(self):
        url = reverse('Address1')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 20)  # 20 is coming from the 20 VDCs we made which each have their own District

    def test_list_all_address1s(self):
        """
            This one doesn't paginate the addresses
        """
        url = reverse('Address1all')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 20)  # 20 is coming from the 20 VDCs we made which each have their own District

    def test_retrieve_address1(self):
        url = reverse('Address1detail', args=[1])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], 1)  # 1 is the arg we passed into the url

    def test_update_address1(self):
        url = reverse('Address1detail', args=[1])
        data = {'name': "updatedAddress1"}
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], 1)  # 1 is the arg we passed into the url
        self.assertEqual(response.data['name'], "updatedAddress1")  # 1 is the arg we passed into the url

    def test_remove_address1(self):
        address1 = DistrictFactory.create()
        url = reverse('Address1detail', args=[address1.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Check that the address doesn't exist anymore
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_address1_403_if_doesnt_have_permission(self):
            self.bad_user = BadVdcUserFactory.create()
            self.client.force_authenticate(user=self.bad_user)

            address2 = CannonicalNameFactory.create()

            # get detail
            url = reverse('Address1detail', args=[address2.id])
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

            # put detail
            url = reverse('Address1detail', args=[address2.id])
            response = self.client.put(url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

            # delete detail
            url = reverse('Address1detail', args=[address2.id])
            response = self.client.delete(url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

            # get
            url = reverse('Address1')
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

            # post
            url = reverse('Address1')
            response = self.client.post(url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)



class Address2Test(APITestCase):

    def setUp(self):
        self.user = VdcUserFactory.create()
        self.client.force_authenticate(user=self.user)

        self.VDCList = VDCFactory.create_batch(20)
        self.factory = APIRequestFactory()
        self.first_district = self.VDCList[0].district
        self.first_cannonical_name = self.VDCList[0].cannonical_name
        self.data = {
            'name': 'Address2',
            "latitude": 29.1837169619,
            "longitude": 81.2336041444,
            "verified": False,
            "district": {
                "id": self.first_district.id,
                "name": self.first_district.name,
            },
            "cannonical_name": {
                "id": self.first_cannonical_name.id,
                "name": self.first_cannonical_name.name,
            },
        }

    def test_create_address2(self):
        url = reverse('Address2')

        response = self.client.post(url, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data['id'])
        self.assertEqual(response.data['name'], 'Address2')
        self.assertEqual(response.data['district']['id'], self.first_district.id)
        self.assertEqual(response.data['cannonical_name']['id'], self.first_cannonical_name.id)

    def test_create_address2_cannonical_name_null(self):
        # Should be able to save address2 with null cannonical name
        url = reverse('Address2')

        self.data["cannonical_name"] = {"id": -1, "name": "Null"}
        response = self.client.post(url, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data['id'])
        self.assertEqual(response.data['name'], 'Address2')
        self.assertEqual(response.data['district']['id'], self.first_district.id)
        self.assertEqual(response.data['cannonical_name'], None)

    def test_update_address2(self):
        address2 = VDCFactory.create()
        url = reverse('Address2detail', args=[address2.id])

        self.data['id'] = address2.id
        self.data['name'] = "Address2Updated"

        response = self.client.put(url, self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Address2Updated')
        self.assertEqual(response.data['id'], address2.id)

    def test_update_address2_cannonical_name_null(self):
        # Should be able to save address2 with null cannonical name
        address2 = VDCFactory.create()
        url = reverse('Address2detail', args=[address2.id])

        self.data['id'] = address2.id
        self.data['name'] = "Address2Updated"
        self.data["cannonical_name"] = {"id": -1, "name": "Null"}

        response = self.client.put(url, self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['id'])
        self.assertEqual(response.data['name'], 'Address2Updated')
        self.assertEqual(response.data['district']['id'], self.first_district.id)
        self.assertEqual(response.data['cannonical_name'], None)

    def test_remove_address2(self):
        address2 = VDCFactory.create()
        url = reverse('Address2detail', args=[address2.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Check that the address doesn't exist anymore
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_address2(self):
        address2 = VDCFactory.create()
        url = reverse('Address2detail', args=[address2.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], address2.id)
        self.assertEqual(response.data['name'], address2.name)

    def test_retrieve_address2_cannonical_name_null(self):
        address2 = CannonicalNameFactory.create()
        url = reverse('Address2detail', args=[address2.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], address2.id)
        self.assertEqual(response.data['name'], address2.name)
        self.assertEqual(response.data['cannonical_name'], None)

    def test_403_if_doesnt_have_permission(self):
        self.bad_user = BadVdcUserFactory.create()
        self.client.force_authenticate(user=self.bad_user)

        address2 = CannonicalNameFactory.create()

        # get detail
        url = reverse('Address2detail', args=[address2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # put detail
        url = reverse('Address2detail', args=[address2.id])
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # delete detail
        url = reverse('Address2detail', args=[address2.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # get
        url = reverse('Address2')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # post
        url = reverse('Address2')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
