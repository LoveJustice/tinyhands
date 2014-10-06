from django.test import TestCase
from dataentry.models import District, VDC
from fuzzy_matching import match_location

class FuzzyLocationMatchingTest(TestCase):
    
    fixtures = ['geo-code-locations.json']

    def test_district_matching_works(self):
        original = District.objects.all()[0].name
        match = match_location(district_name=original)
        self.assertEquals(original,match.name)

    def test_district_match_found_if_one_character_off(self):
        original = District.objects.all()[0].name
        close_name = original + "s"
        match = match_location(district_name=close_name)
        self.assertEquals(original,match.name)

    def test_no_district_match_on_bad_name(self):
        name = "xyzxyz"
        district_match = match_location(district_name=name)
        self.assertEquals(district_match, None)

    def test_vdc_matching_works(self):
        original = VDC.objects.all()[0].name
        match = match_location(vdc_name=original)
        self.assertEquals(original, match.name)

    def test_vdc_match_found_if_one_character_off(self):
        original = VDC.objects.all()[0].name
        close_name = original + "s"
        match = match_location(vdc_name=close_name)
        self.assertEquals(original, match.name)

    def test_no_vdc_match_on_bad_name(self):
        name = "xyzxyz"
        match = match_location(vdc_name=name)
        self.assertEquals(match, None)
