import copy
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from dataentry.models import Permission, UserLocationPermission

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('FromPermissionGroup', nargs='+', type=str)
        parser.add_argument('ToPermissionGroup', nargs='+', type=str)
        parser.add_argument('CountryName', nargs='+', type=str)
        
    def handle(self, *args, **options):
        from_permission_group = options.get('FromPermissionGroup')[0]
        to_permission_group = options.get('ToPermissionGroup')[0]
        country_name = options.get('CountryName')[0]
        
        if country_name == 'GLOBAL':
            user_permissions = UserLocationPermission.objects.filter(permission__permission_group = from_permission_group)
            self.copy_permissions(user_permissions, to_permission_group, 'GLOBAL')
        else:
            user_permissions = UserLocationPermission.objects.filter(permission__permission_group = from_permission_group,
                                                                    country__name=country_name)
            self.copy_permissions(user_permissions, to_permission_group, 'COUNTRY')
            user_permissions = UserLocationPermission.objects.filter(permission__permission_group = from_permission_group,
                                                                    station__operating_country__name=country_name)
            self.copy_permissions(user_permissions, to_permission_group, 'STATION')
            
    def copy_permissions(self, user_permissions, to_permission_group, mode):
        for user_permission in user_permissions:
            permission = Permission.objects.get(permission_group=to_permission_group,
                                                action=user_permission.permission.action)
            try:
                if mode == 'GLOBAL':
                    UserLocationPermission.objects.get(account=user_permission.account,
                                    permission=permission)
                elif mode == 'COUNTRY':
                    UserLocationPermission.objects.get(account=user_permission.account,
                                    country = user_permission.country,
                                    permission=permission)
                elif mode == 'STATION':
                    UserLocationPermission.objects.get(account=user_permission.account,
                                    station = user_permission.station,
                                    permission=permission)
            except ObjectDoesNotExist:
                new_permission = UserLocationPermission()
                new_permission.account = user_permission.account
                new_permission.country = user_permission.country
                new_permission.station = new_permission.station
                new_permission.permission = permission
                new_permission.save()
             
        