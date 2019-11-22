import json
import datetime

from django.conf import settings
from django.core.management import call_command
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.tests.factories import BadIrfUserFactory, SuperUserFactory
from dataentry.tests.factories import IrfIndiaFactory, MbzStationFactory, PersonFactory
from dataentry.models import Form, IrfIndia, IntercepteeIndia
from dataentry.form_data import FormData, CardData, FormCategory
from dataentry.serialize_form import FormDataSerializer

from static_border_stations.tests.factories import GenericUserWithPermissions

class IrfTest(APITestCase):
    fixtures = ['initial-required-data/Country.json', 'initial-required-data/Permission.json']
    def setUp(self):
        form_data_file = settings.BASE_DIR + '/fixtures/initial-required-data/form_data.json'
        call_command('loaddata', form_data_file, verbosity=0)
        self.irf_list = IrfIndiaFactory.create_batch(20)
        self.user = GenericUserWithPermissions.create([{'group':'IRF', 'action':'VIEW', 'country': None, 'station': None},
                                                       {'group':'IRF', 'action':'EDIT', 'country': None, 'station': None},
                                                       {'group':'IRF', 'action':'ADD', 'country': None, 'station': None}])
        self.client.force_authenticate(user=self.user)
        self.form = Form.objects.get(form_name='irfIndia')
        self.form.stations.add(MbzStationFactory())

    def test_list_irfs(self):
        url = reverse('irfNew')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 20)

    def test_doesnt_have_permission(self):
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
        station_id = irf_entry['station']['id']
        irf_number = irf_entry['irf_number']
        
        url = reverse('irfNewDetail', args=[station_id, irf_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['station_id'],station_id)
        self.assertEqual(response.data['storage_id'], irf_id)
        
    def test_irf_put_fail_validation(self):
        irf_qs = IrfIndia.objects.all()
        irf = irf_qs[0]
        form = Form.current_form('IRF', irf.station.id)
        form_data = FormData(irf, form)
          
        serializer = FormDataSerializer(form_data, context={})
        put_data = {'main':json.dumps(serializer.data)}
        url = reverse('irfNewDetail', args=[irf.station.id, irf.id])
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
        irf.number_of_victims = 1
        irf.number_of_traffickers = 0
        irf.logbook_received = datetime.datetime.now().date()
        
        irf.evidence_categorization = 'Some Evidence of Trafficking'
        irf.reason_for_intercept = 'Primary reason'
        irf.convinced_by_police = 'Police convinced or forced to stop'
        form = Form.current_form('IRF', irf.station.id)
        form_data = FormData(irf, form)
        
        form_category = FormCategory.objects.get(form=form, name='Interceptees')
        category = form_category.category
         
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
        url = reverse('irfNewDetail', args=[irf.station.id, irf.id])
        response = self.client.put(url, put_data)
          
        if response.status_code != status.HTTP_200_OK:
            print ('test_irf_put', response.data)
          
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        
        
        
