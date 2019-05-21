from django.core.management.base import BaseCommand
from django.db import transaction

from dataentry.models import Category, QuestionLayout

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('CategoryId', nargs='+', type=str)
        
    def handle(self, *args, **options):
        old_category_id = options.get('CategoryId')[0]
        
        
        category = Category.objects.get(id=old_category_id)
        
        with transaction.atomic():
            new_category = Category.objects.get(id=category.id)
            new_category.id = None
            new_category.description = new_category.description + ' copy'
            new_category.save()
                
            question_layouts = QuestionLayout.objects.filter(category=category)
            for question_layout in question_layouts:
                new_question_layout = QuestionLayout.objects.get(id=question_layout.id)
                new_question_layout.id = None
                new_question_layout.category = new_category
                new_question_layout.save()
            
        
        print ('new category id=', new_category.id)
                    
        
        
        
        