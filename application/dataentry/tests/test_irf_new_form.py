import json

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.tests.factories import BadIrfUserFactory, SuperUserFactory
from dataentry.tests.factories import IrfIndiaFactory, PersonFactory
from dataentry.models import Form, IrfIndia, IntercepteeIndia
from dataentry.form_data import FormData, CardData, Category
from dataentry.serialize_form import FormDataSerializer

from static_border_stations.tests.factories import GenericUserWithPermissions

class IrfTest(APITestCase):
    def setUp(self):
        self.irf_list = IrfIndiaFactory.create_batch(20)
        self.user = GenericUserWithPermissions.create([{'group':'IRF', 'action':'VIEW', 'country': None, 'station': None},
                                                       {'group':'IRF', 'action':'EDIT', 'country': None, 'station': None},
                                                       {'group':'IRF', 'action':'ADD', 'country': None, 'station': None}])
        self.client.force_authenticate(user=self.user)

    def test_list_irfs(self):
        url = reverse('irfNew')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 20)

    def test_irf_403_if_doesnt_have_permission(self):
        self.bad_user = GenericUserWithPermissions.create([])
        self.client.force_authenticate(user=self.bad_user)

        # get
        url = reverse('irfNew')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
    
    def test_irf_detail(self):
        url = reverse('irfNew')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        irf_entry = response.data['results'][1]
        irf_id = irf_entry['id']
        country_id = irf_entry['station']['operating_country']['id']
        irf_number = irf_entry['irf_number']
        
        url = reverse('irfNewDetail', args=[country_id, irf_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['country_id'], country_id)
        self.assertEqual(response.data['storage_id'], irf_id)
        
    def test_irf_put_fail_validation(self):
        irf_qs = IrfIndia.objects.all()
        irf = irf_qs[0]
        form = Form.current_form('IRF', irf.station.operating_country.id)
        form_data = FormData(irf, form)
          
        serializer = FormDataSerializer(form_data, context={})
        put_data = {'main':json.dumps(serializer.data)}
        url = reverse('irfNewDetail', args=[irf.station.operating_country.id, irf.id])
        response = self.client.put(url, put_data)
          
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
         
    def gen_put_data(self):
        irf_qs = IrfIndia.objects.all()
        irf = irf_qs[0]
        irf.caught_in_lie = True
        irf.who_noticed = 'contact'
        irf.type_of_intercept = 'suspected'
        irf.contact_paid = True
        irf.which_contact = 'Bus driver'
        form = Form.current_form('IRF', irf.station.operating_country.id)
        form_data = FormData(irf, form)
         
        category = Category.objects.get(form=form, name='Interceptees')
         
        interceptee = IntercepteeIndia()
        interceptee.interception_record = irf
        interceptee.kind = 'v'
        interceptee.person = PersonFactory.create()
         
        card_data = CardData(interceptee, form_data.category_form_dict[category.id], form_data=form_data)
         
        if form_data.card_dict[category.id] is None:
            form_data.card_dict[category.id] = []
         
        form_data.card_dict[category.id].append(card_data)
        
        return form_data
         
    def test_irf_put(self):
        form_data = self.gen_put_data()
        irf = form_data.form_object
        serializer = FormDataSerializer(form_data, context={})
        put_data = {'main':json.dumps(serializer.data)}
        url = reverse('irfNewDetail', args=[irf.station.operating_country.id, irf.id])
        response = self.client.put(url, put_data)
          
        if response.status_code != status.HTTP_200_OK:
            print ('test_irf_put', response.data)
          
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        
        
        
