import os
from django.core.management import call_command
from django.core.exceptions import ObjectDoesNotExist
from .form import Form
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
    def unload_prior(apps, schema_editor):
        for model_name in reversed(FormMigration.form_model_names):
            my_model = apps.get_model('dataentry', model_name)
            my_model.objects.all().delete()
    
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
        fixture_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../fixtures'))
        file_path = fixture_dir + '/' + fixture_filename
        if os.access(file_path, os.R_OK):
            reference_list = FormMigration.get_form_to_station_references()
            FormMigration.unload_prior(apps, schema_editor)
            FormMigration.load_fixture(apps, schema_editor, fixture_dir, fixture_filename)
            FormMigration.restore_form_to_station_references(reference_list)
        else:
            print('Fixture ' + file_path + 'not found - skipping form migration')