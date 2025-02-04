from django.core.management.base import BaseCommand

import json
from dataentry.specification.form_spec_generate import generate_form_spec
from dataentry.specification.irf_spec import irf_202408


class Command(BaseCommand):
    def handle(self, *args, **options):
        results  = generate_form_spec(irf_202408)
        version = results['version'].replace('.','_')
        tag_string = 'tags_' + results['form_type'] + '_' + version
        sep = "='"
        for tag in results['main_tags']:
            tag_string += sep + tag
            sep = "' | '"
        tag_string += "'"
        print(tag_string)
        for card_name in results['card_tags'].keys():
            tag_string = 'tags_' + results['form_type'] + '_' + version + '_' + card_name
            sep = "='"
            for tag in results['card_tags'][card_name]:
                tag_string += sep + tag
                sep = "' | '"
            tag_string += "'"
            print(tag_string)
        for error in results['errors']:
            print (error)