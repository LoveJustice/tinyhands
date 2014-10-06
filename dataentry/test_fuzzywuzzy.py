from django.test import TestCase
from dataentry.models import District, VDC
from fuzzywuzzy import process
from fuzzy_matching import match_location

class FuzzyLocationMatchingTest(TestCase):
    
    fixtures = ['geo-code-locations.json']

    def test_district_matching_works(self):
        original = District.objects.all()[0].name
        match = match_location(district_name=original)
        self.assertEquals(original,match.name)

    def test_district_match_found_if_one_character_off(self):
        original = District.objects.all()[0].name
        closeName = original + "s"
        match = match_location(district_name=closeName)
        self.assertEquals(original,match.name)

    def test_vdc_matching_works(self):
        original = VDC.objects.all()[0].name
        match = match_location(vdc_name=original)
        self.assertEquals(original, match.name)
