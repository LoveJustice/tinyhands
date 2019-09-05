from django.core.management.base import BaseCommand

from dataentry.models import Form
from dataentry.form_data import FormData
from export_import.photo_anonymizer import anonymize_photo_receiver

class Command(BaseCommand):    
    def handle(self, *args, **options):
        forms = Form.objects.filter(form_type__name='IRF')
        for form in  forms:
            mod = __import__(form.storage.module_name, fromlist=[form.storage.form_model_name])
            irf_model = getattr(mod, form.storage.form_model_name, None)
            
            irfs = irf_model.objects.all()
            for irf in irfs:
                form_data = FormData(irf, form)
                anonymize_photo_receiver(None, form_data)
                
                    
        
        
        
        