from django.test import TestCase
from dataentry.models import District, VDC
from dataentry.fuzzy_matching import match_location


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

    def test_vdc_matching_works(self):
        original = VDC.objects.all()[0]
        matches = match_location(vdc_name=original.name)
        self.assertEquals(original, matches[0])

    def test_vdc_match_found_if_one_character_off(self):
        original = VDC.objects.all()[0]
        close_name = original.name + "s"
        matches = match_location(vdc_name=close_name)
        self.assertEquals(original, matches[0])
