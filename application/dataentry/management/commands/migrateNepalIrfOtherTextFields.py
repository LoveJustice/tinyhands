from django.db import connection
from django.core.management.base import BaseCommand
from django.core.management.color import no_style

from dataentry.models import BorderStation, InterceptionRecord, IrfNepal, Interceptee, IntercepteeNepal
from static_border_stations.models import Location

class Command(BaseCommand):
    @staticmethod
    def process_other_checkbox_value(source, dest, name, config):
        other_text_field = config.get('other_text_field')
        other_value = getattr(source, other_text_field)
        setattr(dest, name, other_value)
      
    def handle(self, *args, **options):
        custom_processing = {
            'other_red_flag':{
                'operation':Command.process_other_checkbox_value,
                'other_text_field':'other_red_flag_value'
            },
            'noticed_other_sign':{
                'operation':Command.process_other_checkbox_value,
                'other_text_field':'noticed_other_sign_value'
            },
        }

        print('Migrating IRFs')
        source_irfs = InterceptionRecord.objects.all()
        for source_irf in source_irfs:
            dest_irf = IrfNepal.objects.get(id = source_irf.id)
            
            for attr in custom_processing:
                config = custom_processing[attr]
                operation = config['operation']
                operation(source_irf, dest_irf, attr, config)
             
            dest_irf.save()
       
        print ('Reset sequences')
        sequence_sql = connection.ops.sequence_reset_sql(no_style(), [IrfNepal])
        with connection.cursor() as cursor:
            for sql in sequence_sql:
                cursor.execute(sql)
                
        print('Migration complete')
                    