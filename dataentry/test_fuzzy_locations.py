from django.test import TestCase
from dataentry.models import District, VDC
from fuzzy_matching import match_location

class FuzzyLocationMatchingTest(TestCase):
    
    fixtures = ['geo-code-locations.json']

    def test_district_matching_works(self):
        original = District.objects.all()[0]
        matches = match_location(district_name=original.name)
        self.assertEquals(original,matches[0])

    def test_district_match_found_if_one_character_off(self):
        original = District.objects.all()[0]
        close_name = original.name + "s"
        matches = match_location(district_name=close_name)
        self.assertEquals(original,matches[0])

    def test_no_district_match_on_bad_name(self):
        name = "xyzxyz"
        matches = match_location(district_name=name)
        self.assertEquals(matches, None)

    def test_vdc_matching_works(self):
        original = VDC.objects.all()[0]
        matches = match_location(vdc_name=original.name)
        self.assertEquals(original, matches[0])

    def test_vdc_match_found_if_one_character_off(self):
        original = VDC.objects.all()[0]
        close_name = original.name + "s"
        matches = match_location(vdc_name=close_name)
        self.assertEquals(original, matches[0])

    def test_no_vdc_match_on_bad_name(self):
        name = "xyzxyz"
        matches = match_location(vdc_name=name)
        self.assertEquals(matches, None)

    def test_vdc_and_district_matching_works(self):
        vdc = VDC.objects.all()[0]
        match = match_location(district_name=vdc.district.name, vdc_name=vdc.name)
        self.assertEquals(vdc, match[0])
        self.assertEquals(vdc.district, match[1])
        
