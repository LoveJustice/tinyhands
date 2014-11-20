from django.test import TestCase
from django_webtest import WebTest
from django.core.urlresolvers import reverse_lazy, reverse
import json

from accounts.tests.factories import *

from accounts.models import Account
from dataentry.models import BorderStation

# Create your tests here.
class BorderStationModelsTests(WebTest):
    
    def setUp(self):
        BorderStation.objects.get_or_create(station_name="Test Station", station_code="TS1")
        self.superuser = SuperUserFactory.create()
        self.viewuser = ViewUserFactory.create()
        print(Account.objects.all())
        
    """
    def test_account_permission_work(self):
        account_list = self.app.get(reverse('account_list'), user=self.superuser)
        self.assertEquals(account_list.status_int, 200)
        
        account_list = self.app.get(reverse('account_list'), user=self.viewuser)
        self.assertEquals(account_list.status_int, 403)
        
        account_edit = account_list.click('Edit')
        account_edit.form['email'] = 'dvcolgan@gmail.com'
        redirect = account_edit.save()
        self.assertEquals(redirect.status_int, 304)
        account_list = redirect.follow()
    """
    
    
    """
    For Bryant
    def test_get_empty_create_borderstation_page(self):
        url = reverse_lazy("borderstations_create")
        print(url)
        response = self.client.get(url)
        print(response.status_code)
        print(response.content)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(len(data), 1)
        
    def test_get_view_borderstation_page(self):
        url = reverse_lazy("borderstations_view", args=[1])
        print(url)
        response = self.client.get(url)
        print(response.status_code)
    """