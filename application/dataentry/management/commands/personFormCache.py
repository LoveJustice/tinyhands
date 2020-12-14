from django.core.management.base import BaseCommand

from dataentry.models import Person, PersonForm, SiteSettings


class Command(BaseCommand):
    def handle(self, *args, **options):
        existing_cached_ids = PersonForm.objects.all().values_list('person__id', flat=True)
        uncached_persons = Person.objects.all().exclude(id__in=existing_cached_ids)
        
        for person in uncached_persons:
            PersonForm.load_cache(person)
        
        print (str(len(uncached_persons)) + ' persons added to the person form cache')
        
        loaded_ids = uncached_persons.values_list('id', flat=True)        
        site_settings = SiteSettings.objects.all()[0]
        try:
            recent_count = site_settings.get_setting_value_by_name('PersonForm_recent')
        except:
            recent_count = 100
        try:
            aged_count = site_settings.get_setting_value_by_name('PersonForm_aged')
        except:
            aged_count = 3000
        
        recent_persons = Person.objects.exclude(id__in=loaded_ids).order_by('-id')
        processed_count = 0
        for person in recent_persons:
            PersonForm.load_cache(person)
            processed_count += 1
            if processed_count >= recent_count:
                break
        
        print (str(processed_count) + ' recent person form cache records have been recached')
        
        aged_cache_records = PersonForm.objects.all().order_by('creation_time', 'id')
        last_id = -1
        processed_count = 0
        for aged_cache_record in aged_cache_records:
            if aged_cache_record.person.id == last_id:
                continue
            PersonForm.load_cache(aged_cache_record.person)
            last_id = aged_cache_record.person.id
            processed_count += 1
            if processed_count >= aged_count:
                break
        
        print (str(processed_count) + ' aged person form cache records have been recached')
            
