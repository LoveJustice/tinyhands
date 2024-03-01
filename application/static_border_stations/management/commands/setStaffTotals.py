import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from django.apps import apps

from static_border_stations.models import Staff


class Command(BaseCommand):
    def handle(self, *args, **options):
        Staff.set_all_totals()