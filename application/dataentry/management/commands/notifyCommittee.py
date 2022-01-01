from templated_email import send_templated_mail

from django.core.management.base import BaseCommand
from django.conf import settings
from dataentry.models import BorderStation, Country
from static_border_stations.models import CommitteeMember
from dataentry.models import UserLocationPermission


class Command(BaseCommand):
    def handle(self, *args, **options):
        countries = Country.objects.all()
        email_sender = settings.SERVER_EMAIL
        ulp1 = UserLocationPermission.objects.filter(permission__permission_group = 'NOTIFICATIONS', permission__action = 'COMMITTEE', station=None, country=None)
        for country in countries:
            stations = BorderStation.objects.filter(operating_country=country, features__contains='hasSubcommittee').order_by("station_name")
            station_list = ''
            for station in stations:
                committee_count = CommitteeMember.objects.filter(border_station=station).count();
                if committee_count < 3:
                    if len(station_list) > 0:
                        station_list += ', '
                    station_list += station.station_name + ' (' + station.station_code + ')'
            
            if len(station_list) > 0:
                ulp2 = UserLocationPermission.objects.filter(permission__permission_group = 'NOTIFICATIONS', permission__action = 'COMMITTEE', station=None, country=country)
                ulp = (ulp1 | ulp2).distinct()
                for user_location_permission in ulp:
                    context = {}
                    context['account'] = user_location_permission.account
                    context['country'] = country.name
                    context['station_list'] = station_list
                    
                    send_templated_mail(
                        template_name='undersized_committee',
                        from_email=email_sender,
                        recipient_list=[user_location_permission.account.email],
                        context=context
                    )