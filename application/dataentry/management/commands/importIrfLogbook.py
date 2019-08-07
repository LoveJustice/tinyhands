import csv
import datetime

from django.core.exceptions import ObjectDoesNotExist

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('irf_class', nargs='+', type=str)
        parser.add_argument('in_file', nargs='+', type=str)
        
    def has_data(self, value):
        if value is not None and value != '' and value != '-':
            return True
        else:
            return False
        
    def process_logbook(self, model, dictReader):
        column_field = {
            "Were there incomplete questions on the IRF that prevented submission?":"logbook_incomplete_questions",
            "Please list incomplete sections that prevented submission":"logbook_incomplete_sections",
            "Notes":"logbook_notes",
            "Date Complete Information was Received":"logbook_information_complete",
            "Verification":"logbook_first_verification",
            "Reason":"logbook_first_reason",
            "Follow-Up Call Completed?":"logbook_followup_call",
            "Date Verification was complete":"logbook_first_verification_date",
            "Reviewed by Leadership":"logbook_leadership_review",
            "Leadership's Verification":"logbook_second_verification",
            "Leaderhip's Reason for Change":"logbook_second_reason",
            "Date Leadership's Verification was Complete":"logbook_second_verification_date"
            }
        date_fields = ["logbook_information_complete", "logbook_first_verification_date", "logbook_second_verification_date"]
        for row in dictReader:
            irf_number = row['IRF Number']
            try:
                irf = model.objects.get(irf_number=irf_number)
                
                for column, field in column_field.items():
                    value = row[column]
                    if value is not None and value != '' and value != '-':
                        if value == 'Not Clear Evidence of Trafficking - But Right to Intercept (because of High Risk of Trafficking)':
                            value = 'High Risk of Trafficking'
                        if field in date_fields:
                            value = datetime.datetime.strptime(value, '%m/%d/%Y').date()
                        setattr(irf, field, value)
                
                if irf.logbook_second_verification == 'Should Not have Intercepted or Should Not have Completed IRF (because there is Not a High Risk of Trafficking)':
                    irf.status = 'invalid'
                elif irf.logbook_second_verification is not None and irf.logbook_second_verification != '':
                    irf.status='second-verification'
                elif irf.logbook_first_verification is not None and irf.logbook_first_verification != '':
                    irf.status='first-verification'
                else:
                    irf.status = 'approved'
                irf.save()
            except ObjectDoesNotExist:
                print ('Unable to find IRF', irf_number)
                pass

    def handle(self, *args, **options):
        in_file = options['in_file'][0]
        
        mod = __import__('dataentry.models', fromlist=[options['irf_class'][0]])
        if mod is None:
            print ('unable to locate module')
            return
        model = getattr(mod, options['irf_class'][0], None)
        if model is None:
            print ('unable to locate model')
            return
        
        with open(in_file) as csvfile:
            reader = csv.DictReader(csvfile)
            self.process_logbook(model, reader)
