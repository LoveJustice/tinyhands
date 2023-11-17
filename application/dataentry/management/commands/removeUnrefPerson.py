from datetime import datetime, timedelta
from django.core.management.base import BaseCommand

from dataentry.models import MasterPerson, Person


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--interval', nargs='+', type=int, help="Number of days prior to current time to check persons based on last modified date")
        
    def handle(self, *args, **options):
        if options['interval']:
            interval = options['interval'][0]
        else:
            interval = None
        
        current = datetime.now()
        end_time = current - timedelta(hours=1)
        print('end time', end_time)
            
        obj = Person.objects.first()
        obj_has_reverse = False
        # reverse relation "fields" on the Reporter model are auto-created and
        # not concrete
        accessors = []
        accessor_count = {}
        skip_accessor=['personform_set', 'personidentification_set', 'matchhistory_set']
        for reverse in [f for f in obj._meta.get_fields() 
                        if f.auto_created and not f.concrete]:
            # in case the related name has been customized
            name = reverse.get_accessor_name()
            if name not in skip_accessor:
                accessors.append(name)
                accessor_count[name] = 0
        
        master_accessors = []
        obj = MasterPerson.objects.first()
        for reverse in [f for f in obj._meta.get_fields() 
                        if f.auto_created and not f.concrete]:
            # in case the related name has been customized
            name = reverse.get_accessor_name()
            if name != 'person_set':
                master_accessors.append(name)
        
        
        remove_count = 0
        processed_count = 0
        persons = Person.objects.filter(last_modified_time__lt=end_time)
        if interval is not None:
            start_time = current - timedelta(days=interval)
            persons = persons.filter(last_modified_time__gt=start_time)
            print('Start time', start_time)
        else:
            print ('Start time None')
        for person in persons:
            can_remove = True
            for accessor in accessors:
                related = getattr(person, accessor, None)
                if related is not None:
                    references = related.all()
                    if len(references) > 0:
                        can_remove = False
                        accessor_count[accessor] += 1
                        
            processed_count += 1
            if can_remove:
                remove_count += 1
                for accesor_remove in skip_accessor:
                    remove_related = getattr(person, accesor_remove, None)
                    if remove_related is not None:
                        references = remove_related.all()
                        for reference in references:
                            reference.delete()
                master_person = person.master_person
                person.delete();
                other_persons =  master_person.person_set.all()
                if len(other_persons) < 1:
                    for master_accessor in master_accessors:
                        related = getattr(master_person, master_accessor, None)
                        references = related.all()
                        for reference in references:
                            reference.delete()
                    master_person.delete()
            
            if processed_count % 1000 == 0:
                print('processed',processed_count, 'remove', remove_count, accessor_count)
                
        print('processed',processed_count, 'remove', remove_count, accessor_count)
            