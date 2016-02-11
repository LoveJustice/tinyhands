from django.core.management.base import BaseCommand
from dataentry.models import *


class Command(BaseCommand):
    help = 'Null out bad foreign keys'

    def handle(self, *args, **options):
        vdc_ids = [vdc.id for vdc in VDC.objects.all()]
        district_ids = [district.id for district in District.objects.all()]

        try:
            bad_foreign_key_district = District.objects.get(name='bad foreign key District')
            bad_foreign_key_vdc = VDC.objects.get(name='bad foreign key VDC')
        except:
            bad_foreign_key_district = District.objects.create(name='bad foreign key District')
            bad_foreign_key_vdc = VDC.objects.create(name='bad foreign key VDC', longitude=0, latitude=0, x.canonical_name=None)

        interceptees_list = Interceptee.objects.all()
        for interceptee in interceptees_list:
            if interceptee.district_id not in district_ids:
                interceptee.district_id = bad_foreign_key_district
            if interceptee.vdc_id not in vdc_ids:
                interceptee.vdc_id = bad_foreign_key_vdc
            interceptee.save()

        victim_interview_list = VictimInterview.objects.all()
        for thing in victim_interview_list:
            if thing.victim_address_district_id not in district_ids:
                thing.victim_address_district_id = bad_foreign_key_district.id
            if thing.victim_guardian_address_district_id not in district_ids:
                thing.victim_guardian_address_district_id = bad_foreign_key_district.id
            if thing.victim_address_vdc_id not in vdc_ids:
                thing.victim_address_vdc_id = bad_foreign_key_vdc.id
            if thing.victim_guardian_address_vdc_id not in vdc_ids:
                thing.victim_guardian_address_vdc_id = bad_foreign_key_vdc.id
            thing.save()


        vif_location_list = VictimInterviewLocationBox.objects.all()
        for thing in vif_location_list:
            if thing.district_id not in district_ids:
                thing.district_id = bad_foreign_key_district.id
            if thing.vdc_id not in vdc_ids:
                thing.vdc_id = bad_foreign_key_vdc.id
            thing.save()

        vif_person_list = VictimInterviewPersonBox.objects.all()
        for thing in vif_person_list:
            if thing.address_district_id not in district_ids:
                thing.address_district_id = bad_foreign_key_district.id
            if thing.address_vdc_id not in vdc_ids:
                thing.address_vdc_id = bad_foreign_key_vdc.id
            thing.save()
