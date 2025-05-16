from pathlib import Path

from django.core.management.base import BaseCommand
from django.conf import settings

from specification.form_spec_generate import generate_form_spec

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('form_type', nargs='+', type=str)
        parser.add_argument('version', nargs='+', type=str)

    def handle(self, *args, **options):
        form_type = options['form_type'][0]
        form_version = options['version'][0]
        spec_name = 'version_specification'
        path_string = settings.BASE_DIR.replace('C:', '/mnt/c')
        directory = Path(path_string).as_posix() + '/specification/' + form_type + '/' + form_version + '/'
        mod = __import__('specification.' + form_type + '.' + form_version, fromlist=[spec_name])
        spec = getattr(mod, spec_name, None)
        results  = generate_form_spec(spec)
        version = results['version'].replace('.','_')
        if len(results['errors']):
            for error in results['errors']:
                print(error)
            exit(1)

        outfile = directory + 'tags.ts'
        with open(outfile, 'w') as f:
            tag_string_base = 'type Tags' + results['form_type'].title() + version
            tag_string = tag_string_base
            sep = ' = "'
            for tag in results['main_tags']:
                tag_string += sep + tag
                sep = '"\n\t| "'
            tag_string += '";'
            print(tag_string, file=f)
            for card_name in results['card_tags'].keys():
                tag_string = tag_string_base + card_name
                sep = '="'
                for tag in results['card_tags'][card_name]:
                    tag_string += sep + tag
                    sep = '"\n\t| "'
                tag_string += '";'
                print(tag_string, file=f)

        outfile = directory + 'client.json'
        with open(outfile, 'w') as f:
            for value in results['client_json'].values():
                print('', file=f)
                print(value, file=f)