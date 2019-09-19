import csv
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from dataentry.models.irf_nepal import IrfNepal
from dataentry.models.vdf_nepal import VdfNepal
from dataentry.models.cif_nepal import CifNepal

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('in_file', nargs='+', type=str)
        
    def has_data(self, value):
        if value is not None and value != '' and value != '-':
            return True
        else:
            return False
    
    def process_logbook(self, dictReader):
        for row in dictReader:
            self.process_irf_logbook(IrfNepal, row)
            self.process_vdf_logbook(VdfNepal, row)
            self.process_cif_logbook(CifNepal, row)
        
        
    def process_irf_logbook(self, irf_class, row):
        column_field = {
            "Date IRF Received":"logbook_received",
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
            "Date Leadership's Verification was Complete":"logbook_second_verification_date",
            "Date IRF Entered":"logbook_submitted",
            "Back Corrected Form":"logbook_back_corrected"
            }
        date_fields = [
            "logbook_received",
            "logbook_information_complete",
            "logbook_first_verification_date",
            "logbook_second_verification_date",
            "logbook_submitted"
            ]
        long_fields = [
            "logbook_notes", "logbook_first_reason", "logbook_second_reason"
            ]

        irf_number = row['Case Number']
        try:
            irf = irf_class.objects.get(irf_number=irf_number)
            
            for column, field in column_field.items():
                value = row[column]
                if value is not None and value != '' and value != '-':
                    if value == 'Not Clear Evidence of Trafficking - But Right to Intercept (because of High Risk of Trafficking)':
                        value = 'High Risk of Trafficking'
                    if field in date_fields:
                        value = datetime.datetime.strptime(value, '%m/%d/%Y').date()
                    elif field not in long_fields and len(value) > 127:
                        value = value[:126]
                    
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
    
    def process_vdf_logbook(self, vdf_class, row):
        column_field = {
            "Date VDF Received":"logbook_received",
            "Date VDF Entered":"logbook_submitted",
            "Date VDF Entered":"logbook_submitted",
            "Were there incomplete questions on the VDF that prevented submission?":"logbook_incomplete_questions",
            "Please list incomplete VDF sections that prevented submission":"logbook_incomplete_sections",
            "Date Complete VDF Information was Received":"logbook_information_complete",
            "VDF Notes":"logbook_notes",
            }
        date_fields = [
            "logbook_received",
            "logbook_information_complete",
            "logbook_submitted"
            ]
        long_fields = [
            "logbook_notes"
            ]
        irf_number = row['Case Number']
        if irf_number is None or irf_number == '' or row['Date VDF Entered'] is None or row['Date VDF Entered'] == '':
            return
            
        vdfs = vdf_class.objects.filter(vdf_number__startswith=irf_number)
        for vdf in vdfs:
            for column, field in column_field.items():
                value = row[column]
                if value is not None and value != '' and value != '-':
                    if field in date_fields:
                        value = datetime.datetime.strptime(value, '%m/%d/%Y').date()
                    elif field not in long_fields and len(value) > 127:
                        value = value[:126]
                    
                    setattr(vdf, field, value)
            vdf.save()

    def process_cif_logbook(self, cif_class, row):
        column_field = {
            "Date CIF Received":"logbook_received",
            "Date CIF Entered":"logbook_submitted",
            "Date CIF Entered":"logbook_submitted",
            "Were there incomplete questions on the CIF that prevented submission?":"logbook_incomplete_questions",
            "Please list incomplete CIF sections that prevented submission":"logbook_incomplete_sections",
            "Date Complete CIF Information was Received":"logbook_information_complete",
            "CIF Notes":"logbook_notes",
            }
        date_fields = [
            "logbook_received",
            "logbook_information_complete",
            "logbook_submitted"
            ]
        long_fields = [
            "logbook_notes"
            ]
        irf_number = row['Case Number']
        if irf_number is None or irf_number == '' or row['Date CIF Entered'] is None or row['Date CIF Entered'] == '':
            return
            
        cifs = cif_class.objects.filter(cif_number__startswith=irf_number)
        for cif in cifs:
            for column, field in column_field.items():
                value = row[column]
                if value is not None and value != '' and value != '-':
                    if field in date_fields:
                        value = datetime.datetime.strptime(value, '%m/%d/%Y').date()
                    elif field not in long_fields and len(value) > 127:
                        value = value[:126]
                    
                    setattr(cif, field, value)
            cif.save()


    def handle(self, *args, **options):
        in_file = options['in_file'][0]
        
        with open(in_file) as csvfile:
            reader = csv.DictReader(csvfile)
            self.process_logbook(reader)
