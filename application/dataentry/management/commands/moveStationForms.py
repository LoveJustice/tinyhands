from django.core.management.base import BaseCommand
from django.db.models import Q
from django.db import transaction

from dataentry.models import BorderStation, Form, FormCategory


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('station_code', nargs='+', type=str)
        parser.add_argument('source_form', nargs='+', type=str)
        
    def handle(self, *args, **options):
        station_code = options.get('station_code')[0]
        source_form = options.get('source_form')[0]
        card_mapping = []
        
        station = BorderStation.objects.get(station_code=station_code)
        
        source_form = Form.objects.get(form_name=source_form)
        source_form_class = source_form.storage.get_form_storage_class()  
        dest_form = Form.objects.get(form_type=source_form.form_type, stations=station)
        dest_form_class = dest_form.storage.get_form_storage_class()  
        
        source_cards = FormCategory.objects.filter(form=source_form).exclude(storage__isnull=True)
        for source_card in source_cards:
            dest_card = FormCategory.objects.get(form=dest_form, name=source_card.name)
            entry = {
                'name':source_card.name,
                'source_class':source_card.storage.get_form_storage_class(),
                'dest_class':dest_card.storage.get_form_storage_class(),
                'foreign_key_name':source_card.storage.foreign_key_field_parent
                }
            card_mapping.append(entry)
        
        source_form_objects = source_form_class.objects.filter(station=station)
        
        for source_form_object in source_form_objects:
            with transaction.atomic():
                old_objs = []
                dest_form_object = dest_form_class()
                self.copy_object(source_form_object, dest_form_object)
                dest_form_object.save()
                
                for card_map in card_mapping:
                    source_class = card_map['source_class']
                    dest_class = card_map['dest_class']
                    foreign_key_name = card_map['foreign_key_name']
                    source_cards = source_class.objects.filter(Q((foreign_key_name, source_form_object)))
                    for source_card in source_cards:
                        dest_card = card_map['dest_class']()
                        self.copy_object(source_card, dest_card)
                        setattr(dest_card, foreign_key_name, dest_form_object)
                        old_objs.append(source_card)
                        dest_card.save()
                        
                old_objs.append(source_form_object)
                for old_obj in old_objs:
                    old_obj.delete()
                
    
    def copy_object(self, source, dest):
        source_dict = source.__dict__
        for member, value in source_dict.items():
            if hasattr(dest, member) and member != 'id':
                setattr(dest, member, value)