from django.core.management.base import BaseCommand
from django.db.models import Q
from django.db import transaction

from dataentry.models import BorderStation, Form, FormCategory, Storage


class Command(BaseCommand):
    form_prefix = ['Irf', 'Cif', 'Vdf']
    card_prefix = [ 
            'Interceptee', 'IrfAttachment',
            'PotentialVictim', 'Transporation', 'PersonBox','LocationBox', 'VehicleBox', 'CifAttachment',
            'VdfAttachment'
        ]
    def add_arguments(self, parser):
        parser.add_argument('form_type', nargs='+', type=str)
    
    def processForm(self, form):
        old_model = form.storage.get_form_storage_class()
        new_model = None
        for prefix in Command.form_prefix:
            if form.storage.form_model_name.startswith(prefix) and form.storage.form_model_name != prefix + 'Common':
                new_storage = Storage.objects.get(form_model_name=prefix + 'Common')
                new_model = new_storage.get_form_storage_class()
                break
        
        if new_model is None:
            print ('Cannot find new model for form ' + form.form_name)
            return False
        
        card_mapping = []
        source_cards = FormCategory.objects.filter(form=form).exclude(storage__isnull=True)
        for source_card in source_cards:
            dest_storage = None
            for prefix in Command.card_prefix:
                if source_card.storage.form_model_name.startswith(prefix):
                    if prefix == 'Transporation':
                        dest_storage = Storage.objects.get(form_model_name='TransportationCommon')
                    else:
                        dest_storage = Storage.objects.get(form_model_name=prefix + 'Common')
                    break
            if dest_storage is None:
                print ('Cannot find common card storage for', source_card.storage.form_model_name)
                return False
            
            entry = {
                'source_card':source_card,
                'source_class':source_card.storage.get_form_storage_class(),
                'dest_storage':dest_storage,
                'dest_class':dest_storage.get_form_storage_class(),
                'foreign_key_name':source_card.storage.foreign_key_field_parent
                }
            card_mapping.append(entry)
        
        source_form_objects = old_model.objects.all()
        
        with transaction.atomic():
            for source_form_object in source_form_objects:
                with transaction.atomic():
                    old_objs = []
                    dest_form_object = new_model()
                    self.copy_object(source_form_object, dest_form_object)
                    dest_form_object.save()
                    dest_form_object.date_time_entered_into_system = source_form_object.date_time_entered_into_system
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
            
            form.storage = new_storage
            form.save()
            for card_map in card_mapping:
                card_map['source_card'].storage = card_map['dest_storage'];
                card_map['source_card'].save()
        
        return True
        
    def handle(self, *args, **options):
        form_type = options.get('form_type')[0]
        
        forms = Form.objects.filter(form_type__name=form_type)
        for form in forms:
            if self.processForm(form) == True:
                print (form.form_name, 'has been moved')
            else:
                print (form.form_name, 'move failed')
                return
                
    
    def copy_object(self, source, dest):
        source_dict = source.__dict__
        for member, value in source_dict.items():
            if hasattr(dest, member) and member != 'id':
                setattr(dest, member, value)