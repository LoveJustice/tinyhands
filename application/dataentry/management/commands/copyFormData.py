from django.core.management.base import BaseCommand
from django.db import transaction

from dataentry.models import Form, Category, CardStorage, QuestionLayout, FormValidation, FormValidationQuestion

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('form', nargs='+', type=str)
        parser.add_argument('newForm', nargs='+', type=str)
        
    def handle(self, *args, **options):
        old_form_name = options.get('form')[0]
        new_form_name = options.get('newForm')[0]
        
        
        old_form = Form.objects.get(form_name=old_form_name)
        
        tmp = Form.objects.filter(form_name=new_form_name)
        if len(tmp) > 0:
            print ("form with name " + new_form_name + " already exists")
            return
        
        with transaction.atomic():
            new_form = Form.objects.get(form_name=old_form_name)
            new_form.id = None
            new_form.form_name = new_form_name
            new_form.save()
            
            categories = Category.objects.filter(form=old_form)
            for category in categories:
                new_category = Category.objects.get(id=category.id)
                new_category.id = None
                new_category.form = new_form
                new_category.save()
                
                card_storages = CardStorage.objects.filter(category=category)
                for card_storage in card_storages:
                    new_card_storage = CardStorage.objects.get(id=card_storage.id)
                    new_card_storage.id = None
                    new_card_storage.category = new_category
                    new_card_storage.save()
                    
                question_layouts = QuestionLayout.objects.filter(category=category)
                for question_layout in question_layouts:
                    new_question_layout = QuestionLayout.objects.get(id=question_layout.id)
                    new_question_layout.id = None
                    new_question_layout.category = new_category
                    new_question_layout.save()
            
            validations = FormValidation.objects.filter(form=old_form)
            for validation in validations:
                new_validation = FormValidation.objects.get(id=validation.id)
                new_validation.id = None
                new_validation.form = new_form
                new_validation.save()
                
                validation_questions = FormValidationQuestion.objects.filter(validation=validation)
                for validation_question in validation_questions:
                    new_validation_question = FormValidationQuestion.objects.get(id=validation_question.id)
                    new_validation_question.id = None
                    new_validation_question.validation = new_validation
                    new_validation_question.save()
        
        print (old_form_name, '=>', new_form_name)
        print ("Remember to add storage entries in dataentry_storage table and then update the storage " 
                "references in the dataentry_form and dataentry_cardstorage for the new form")
                    
        
        
        
        