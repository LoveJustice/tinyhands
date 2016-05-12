from django.core.management.base import BaseCommand
from dataentry.models import *
from dataentry.tests.factories import IrfFactory

class Command(BaseCommand):
    help = 'clean up the bad foreign keys'

    def get_or_create_default_address1(self):
        try:
            d = Address1.objects.get(name='Bad foreign Key Address1')
        except:
            d = Address1.objects.create(name='Bad foreign Key Address1')
        return d

    def get_or_create_default_address2(self, address1):
        try:
            v = Address2.objects.get(name='Bad foreign Key Address2')
        except:
            v = Address2.objects.create(name='Bad foreign Key Address2', latitude=0, longitude=0, address1=address1)
        return v

    def get_or_create_default_irf(self):
        try:
            irf = InterceptionRecord.objects.get(location="Bad foreign Key IRF")
        except:
            irf = IrfFactory.create(location="Bad foreign Key IRF")
        return irf

    def handle(self, *args, **options):
        items = [
            [Person,['address1'],['address2']],
            [VictimInterview,['victim__address1','victim_guardian_address1'],['victim__address2', 'victim_guardian_address2']],
            [VictimInterviewPersonBox,['person__address1'],['person__address2']],
            [VictimInterviewLocationBox,['address1'],['address2']]
        ]

        valid_address2s = [address2.id for address2 in Address2.objects.all()]
        valid_address1s = [address1.id for address1 in Address1.objects.all()]

        default_irf = self.get_or_create_default_irf()
        default_address1 = self.get_or_create_default_address1()
        default_address2 = self.get_or_create_default_address2(default_address1)

        for item in items:
            model = item[0]
            for address1 in item[1]:
                filter_field = address1 + "__in"
                bad_ones = model.objects.exclude(**{filter_field: valid_address1s})
                for x in bad_ones:
                    setattr(x, address1 + '_id', default_address1.id)
                    x.save()
            model = item[0]
            for address2 in item[2]:
                filter_field = address2 + "__in"
                bad_ones = model.objects.exclude(**{filter_field: valid_address2s})
                for x in bad_ones:
                    setattr(x, address2 + '_id', default_address2.id)
                    x.save()


        #  The IRF process is a little different so I had to do it separately down here.
        valid_irfs = [irf.id for irf in InterceptionRecord.objects.all()]
        # irfId_interceptee = [[interceptee.interception_record_id, interceptee] for interceptee in Interceptee.objects.all()]
        for interceptee in Interceptee.objects.all():
            if interceptee.interception_record_id not in valid_irfs:
                interceptee.interception_record_id = default_irf.id
                interceptee.save()
                print("invalid Interceptee!", interceptee)
