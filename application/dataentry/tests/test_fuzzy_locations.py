from django.test import TestCase
from dataentry.models import District, VDC
from dataentry.fuzzy_matching import match_location
from dataentry.tests.factories import VDCFactory


class FuzzyLocationMatchingTest(TestCase):
    def setUp(self):
        self.VDCList = VDCFactory.create_batch(20)

    def test_district_matching_works(self):
        original = District.objects.all()[0]
        matches = match_location(district_name=original.name)
        self.assertEquals(original, matches[0])

    def test_district_match_found_if_one_character_off(self):
        original = District.objects.all()[0]
        close_name = original.name + "s"
        matches = match_location(district_name=close_name)
        self.assertEquals(original, matches[0])

    def test_vdc_matching_works(self):
        original = VDC.objects.all()[0]
        matches = match_location(vdc_name=original.name)
        self.assertEquals(original, matches[0])

    def test_vdc_match_found_if_one_character_off(self):
        original = VDC.objects.all()[0]
        close_name = original.name + "s"
        matches = match_location(vdc_name=close_name)
        self.assertEquals(original, matches[0])
    
    def test_filter_by_district(self):
        VDC.objects.all().delete()
        VDCFactory.create_batch(20)
        
        original = VDC.objects.all()[0]     
        self.VDCList = VDCFactory.create_batch(20)
        matches = match_location(original.district.name, original.name)

        # VDCFactory associates a new District with each VDC
        self.assertEquals(len(matches), 1)

    def test_filter_by_district_multiple_vdcs(self):    
        VDC.objects.all().delete()
        VDCFactory.create_batch(20)
        # Associate a new VDC with the first VDCs District
        original = VDC.objects.all()[0]     
        second = VDC.objects.all()[1]
        second.district = original.district
        second.save()

        # Now there should only be 2 valid VDCs for this district
        matches = match_location(original.district.name, original.name)
        self.assertEquals(len(matches), 2)
