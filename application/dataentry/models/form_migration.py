import os
from django.core.management import call_command
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.color import no_style
from django.db import connection
from .form import Form, FormVersion
from .border_station import BorderStation

class FormMigration:
    form_model_names = [
        'FormType',
        'Storage',
        'Form',
        'CategoryType',
        'Category',
        'CardStorage',
        'AnswerType',
        'Question',
        'QuestionLayout',
        'QuestionStorage',
        'Answer',
        'FormValidationLevel',
        'FormValidationType',
        'FormValidation',
        'FormValidationQuestion',
        'ExportImport',
        'ExportImportCard',
        'ExportImportField',
        'GoogleSheetConfig',
        ]
    
    # preserve existing connections between form and border stations
    @staticmethod
    def get_form_to_station_references():
        reference_list = []
        forms = Form.objects.all()
        for form in forms:
            stations = form.stations.all()
            for station in stations:
                reference_list.append({'form_name':form.form_name, 'station_code':station.station_code})
            
        return reference_list

    @staticmethod
    def load_fixture(apps, schema_editor, fixture_dir, fixture_filename):
        fixture_file = os.path.join(fixture_dir, fixture_filename)
        call_command('loaddata', fixture_file)
    
    @staticmethod
    def unload_prior(apps):
        class_models = []
        for model_name in reversed(FormMigration.form_model_names):
            my_model = apps.get_model('dataentry', model_name)
            class_models.append(my_model)
            my_model.objects.all().delete()
            
        sequence_sql = connection.ops.sequence_reset_sql(no_style(), class_models)
        with connection.cursor() as cursor:
            for sql in sequence_sql:
                cursor.execute(sql)
    
    # restore connections between form and border stations
    @staticmethod
    def restore_form_to_station_references(reference_list):
        for reference in reference_list:
            try:
                form = Form.objects.get(form_name=reference['form_name'])
                try:
                    station = BorderStation.objects.get(station_code=reference['station_code'])
                    form.stations.add(station)
                except ObjectDoesNotExist:
                    print ('Unable for find station to restore reference from form ' + reference['form_name'] + 
                           ' to station with code ' + reference['station_code'])
            except ObjectDoesNotExist:
                print ('Unable for find form to restore reference from form ' + reference['form_name'] + 
                           ' to station with code ' + reference['station_code'])

    @staticmethod
    def migrate(apps, schema_editor, fixture_filename):
        # No longer used, but old migrations still reference this method
        return
#         fixture_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../fixtures'))
#         file_path = fixture_dir + '/' + fixture_filename
#         if os.access(file_path, os.R_OK):
#             reference_list = FormMigration.get_form_to_station_references()
#             FormMigration.unload_prior(apps)
#             FormMigration.load_fixture(apps, schema_editor, fixture_dir, fixture_filename)
#             FormMigration.restore_form_to_station_references(reference_list)
#         else:
#             print('Fixture ' + file_path + 'not found - skipping form migration')
    
        
    @staticmethod
    def check_load_form_data(apps, file_name, checksum_list):
        if len(checksum_list) != 2:
            print('Invalid checksum list', checksum_list)
            return
        
        try:
            form_version = FormVersion.objects.get(id=1)
            if form_version.checksum == int(checksum_list[0]) and form_version.blocks == int(checksum_list[1]):
                print('Checksum values match - no need to reload form data')
                return
        except Exception:
            form_version = FormVersion()
            form_version.id = 1
        
        print('Reloading form data') 
        reference_list = FormMigration.get_form_to_station_references()
        FormMigration.unload_prior(apps)
        call_command('loaddata', file_name) 
        FormMigration.restore_form_to_station_references(reference_list)
        
        form_version.checksum = int(checksum_list[0])
        form_version.blocks = int(checksum_list[1])
        form_version.save()