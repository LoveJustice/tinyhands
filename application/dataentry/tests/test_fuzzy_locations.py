from django.test import TestCase
from dataentry.models import Address1, Address2
from dataentry.fuzzy_matching import match_location
from dataentry.tests.factories import Address2Factory


class FuzzyLocationMatchingTest(TestCase):
    def setUp(self):
        self.Address2List = Address2Factory.create_batch(20)

    def test_district_matching_works(self):
        original = Address1.objects.all()[0]
        matches = match_location(district_name=original.name)
        self.assertEquals(original, matches[0])

    def test_district_match_found_if_one_character_off(self):
        original = Address1.objects.all()[0]
        close_name = original.name + "s"
        matches = match_location(district_name=close_name)
        self.assertEquals(original, matches[0])

    def test_address2_matching_works(self):
        original = Address2.objects.all()[0]
        matches = match_location(vdc_name=original.name)
        self.assertEquals(original, matches[0])

    def test_address2_match_found_if_one_character_off(self):
        original = Address2.objects.all()[0]
        close_name = original.name + "s"
        matches = match_location(vdc_name=close_name)
        self.assertEquals(original, matches[0])

    def test_filter_by_district(self):
        Address2.objects.all().delete()
        Address2Factory.create_batch(20)

        original = Address2.objects.all()[0]
        self.Address2List = Address2Factory.create_batch(20)
        matches = match_location(original.district.name, original.name)

        # Address2Factory associates a new Address1 with each Address2
        self.assertEquals(len(matches), 1)

    def test_filter_by_district_multiple_vdcs(self):
        Address2.objects.all().delete()
        Address2Factory.create_batch(20)
        # Associate a new Address2 with the first Address2s Address1
        original = Address2.objects.all()[0]
        second = Address2.objects.all()[1]
        second.district = original.district
        second.save()

        # Now there should only be 2 valid Address2s for this district
        matches = match_location(original.district.name, original.name)
        self.assertEquals(len(matches), 2)
