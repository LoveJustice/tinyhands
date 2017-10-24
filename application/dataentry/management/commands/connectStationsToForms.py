from django.core.management.base import BaseCommand
from dataentry.models import *

class Command(BaseCommand):
    help = 'connect station objects to IRFs & VIFs'

    def handle(self, *args, **options):
        irfs = InterceptionRecord.objects.filter(border_station=None)
        vifs = VictimInterview.objects.filter(border_station=None)
        print("Staged IRFs: ", len(irfs))
        print("Staged VIFs: ", len(vifs))
        unmatched_irfs = []
        unmatched_vifs = []
        for irf in irfs:
            matching_station = BorderStation.objects.get(station_code=irf.irf_number[:3].upper())
            if matching_station is not None:
                irf.border_station = matching_station
                irf.save()
            else:
                unmatched_irfs.append(irf.irf_number)
        for vif in vifs:
            matching_station = BorderStation.objects.get(station_code=vif.vif_number[:3].upper())
            if matching_station is not None:
                vif.border_station = matching_station
                vif.save()
            else:
                unmatched_vifs.append(vif.vif_number)
        print("Unmatched IRFs: ", unmatched_irfs)
        print("Unmatched VIFs: ", unmatched_vifs)