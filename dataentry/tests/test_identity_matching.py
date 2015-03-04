from django.test import TestCase
from django_webtest import WebTest
from dataentry.models import Interceptee
from dataentry.tests.factories import IntercepteeFactory
from accounts.tests.factories import SettingFactory

import ipdb

class IdentityMatchingModelTests(TestCase):
    def setUp(self):
        self.fuzzy_limit = SettingFactory.create(keyword="Fuzzy-Limit", value=5, description="fuzzy limit")
        self.fuzzy_score_cutoff = SettingFactory.create(keyword="Fuzzy-Score-Cutoff", value=50, description="fuzzy score cutoff")
        self.fuzzy_age_weight = SettingFactory.create(keyword="Fuzzy-Age-Weight", value=1, description="fuzzy age weight")
        self.fuzzy_phone_weight = SettingFactory.create(keyword="Fuzzy-Phone-Number-Weight", value=1, description="fuzzy phone number weight")
        self.interceptee = IntercepteeFactory.create(name="Matt",age=20,phone='1234567890')
        self.interceptee2 = IntercepteeFactory.create(name="Bob",age=35,phone='1112223333')
        self.intercepteeManager = Interceptee.objects
    
    def test_fuzzy_match_on_name(self):
        real_name = self.interceptee.canonical_name.value
        matches = self.intercepteeManager.fuzzy_match_on(real_name)
        self.assertEquals(matches[0][2], self.interceptee)
        
        close_name = real_name+"x"
        matches2 = self.intercepteeManager.fuzzy_match_on(close_name)
        self.assertEquals(matches2[0][2], self.interceptee)
        
    def test_fuzzy_match_on_age(self):
        real_age = self.interceptee.canonical_age.value
        matches = self.intercepteeManager.fuzzy_match_on(input_age=real_age)
        self.assertEquals(matches[0][2], self.interceptee)
        
        close_age = real_age+1
        matches2 = self.intercepteeManager.fuzzy_match_on(input_age=close_age)
        self.assertEquals(matches2[0][2], self.interceptee)
        
    def test_fuzzy_match_on_phone(self):
        real_phone = self.interceptee.canonical_phone.value
        matches = self.intercepteeManager.fuzzy_match_on(input_phone=real_phone)
        self.assertEquals(matches[0][2], self.interceptee)
        
        p = list(real_phone)
        p[0] = '9'
        close_phone = "".join(p)
        matches2 = self.intercepteeManager.fuzzy_match_on(input_phone=close_phone)
        self.assertEquals(matches2[0][2], self.interceptee)
        