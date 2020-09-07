import csv
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from accounts.models import Account
from dataentry.models import MasterPerson, MatchType
from dataentry.views import MasterPersonViewSet

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('mode', nargs='+', type=str)
        parser.add_argument('filename', nargs='+', type=str)
        parser.add_argument('email', nargs='+', type=str)
        parser.add_argument('notes', nargs='+', type=str)
        
    def handle(self, *args, **options):
        mode = options.get('mode')[0]
        file_name = options.get('filename')[0]
        email = options.get('email')[0]
        notes = options.get('notes')[0]
        
        account = Account.objects.get(email=email)
        
        if mode == 'confirmed':
            self.link_confirmed(file_name, account, notes)
        else:
            self.link_pending(mode, file_name, account, notes)

    def link_confirmed(self, file_name, account, notes):
        with open(file_name) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['new_mid'] == row['old_mid']:
                    continue
                data = {'notes':notes}
                master1 = MasterPerson.objects.get(id=int(row['new_mid']))
                master2 = MasterPerson.objects.get(id=int(row['old_mid']))
                data['full_name'] = row['full_name']
                for element in ['birthdate','estimated_birthdate','gender','nationality']:
                    tmp = getattr(master1, element, None)
                    if tmp is None:
                        tmp = getattr(master2, element, None)
                    data[element] = tmp
               
                MasterPersonViewSet.merge_master_persons_base(master1.id, master2.id, account, data)
    
    def link_pending(self, mode, file_name, account, notes):
        match_type = MatchType.objects.get(name=mode)
        
        with open(file_name) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data = {
                    'match_type':match_type.id,
                    'master1':int(row['mid_a']),
                    'master2':int(row['mid_b'])
                    }
                MasterPersonViewSet.create_match_base(account, data)
            