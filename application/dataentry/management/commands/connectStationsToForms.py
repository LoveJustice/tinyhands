from django.core.management.base import BaseCommand
from dataentry.models import *


class Command(BaseCommand):
    help = 'connect station objects to IRFs'

    def handle(self, *args, **options):
        irfs = InterceptionRecord.objects.filter(border_station=None)
        print("Staged IRFs: ", len(irfs))
        unmatched_irfs = []
        for irf in irfs:
            matching_station = BorderStation.objects.get(
                station_code=irf.irf_number[:3].upper())
            if matching_station is not None:
                irf.border_station = matching_station
                irf.save()
            else:
                unmatched_irfs.append(irf.irf_number)
        print("Unmatched IRFs: ", unmatched_irfs)
