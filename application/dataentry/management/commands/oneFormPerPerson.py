from django.core.management.base import BaseCommand
from django.db.models import Q

from dataentry.models import IntercepteeCommon
from dataentry.models import CifCommon, PersonBoxCommon, PotentialVictimCommon, PersonForm
from dataentry.models import VdfCommon
from dataentry.models import LegalCaseSuspect, LegalCaseVictim


class Command(BaseCommand):
    def handle(self, *args, **options):
        check_classes = {
                IntercepteeCommon:'person',
                CifCommon:'main_pv',
                PotentialVictimCommon:'person',
                PersonBoxCommon:'person',
                VdfCommon:'victim',
                LegalCaseSuspect:'person',
                LegalCaseVictim:'person'}
        
        processed_classes = []
        
        for the_class, field_name in check_classes.items():
            processed_classes.append(the_class)
            records = the_class.objects.all()
            for record in records:
                person = getattr(record, field_name)
                if person is None:
                    continue
                match_id = person.id
                for check_class, check_field in check_classes.items():
                    if check_class in processed_classes:
                        continue
                    matches = check_class.objects.filter(Q(**{check_field + '__id':match_id}))
                    for match in matches:
                        person.id = None
                        person.save()
                        setattr(match, check_field, person)
                        print ('Updating',check_class, match.id, match_id)
                        match.save()
                    
                    if len(matches) > 0:
                        PersonForm.objects.filter(person__id=match_id).delete()
                        
            
