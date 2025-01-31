from django.core.management.base import BaseCommand

import json
from dataentry.specification.form_spec_generate import generate_form_spec
from dataentry.specification.irf_spec1 import irf_202408


class Command(BaseCommand):
    def handle(self, *args, **options):
        results  = generate_form_spec(irf_202408)
        tag_string = results['form_type'] + '_' + results['version']
        sep = "='"
        for tag in results['main_tags']:
            tag_string += sep + tag
            sep = "' | '"
        tag_string += "'"
        print(tag_string)
        for (card_name, tag_list) in results['card_tags']:
            tag_string = results['form_type'] + '_' + results['version'] + '_' + card_name
            sep = "='"
            for tag in tag_list:
                tag_string += sep + tag
                sep = "' | '"
            tag_string += "'"
            print(tag_string)
        for error in results['errors']:
            print (error)