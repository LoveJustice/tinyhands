import csv
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from dataentry.models.form import Form

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('base_form_name', nargs='+', type=str)
        parser.add_argument('in_file', nargs='+', type=str)
        parser.add_argument(
            '--dateFormat',
            action='append',
            type=str,
        )
        
    def has_data(self, value):
        if value is not None and value != '' and value != '-':
            return True
        else:
            return False
        
    def parse_date(self, date_string):
        value = None
        for date_format in self.date_formats:
            try:
                value = datetime.datetime.strptime(date_string, date_format).date()
                break
            except:
                pass
            
        if value is None:
            print ('Unable to parse date string ' + date_string,self.date_formats)
            
        return value
    
    def process_logbook(self, dictReader, irf_class, cif_class, vdf_class):
        
        for row in dictReader:
            self.process_irf_logbook(irf_class, row)
            self.process_vdf_logbook(vdf_class, row)
            self.process_cif_logbook(cif_class, row)
        
        
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
            "Leadership's Verification":"verified_evidence_categorization",
            "Leaderhip's Reason for Change":"logbook_second_reason",
            "Date Leadership's Verification was Complete":"verified_date",
            "Date IRF Entered":"logbook_submitted",
            "Back Corrected Form":"logbook_back_corrected"
            }
        date_fields = [
            "logbook_received",
            "logbook_information_complete",
            "logbook_first_verification_date",
            "verified_date",
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
                        value = self.parse_date(value)
                    elif field not in long_fields and len(value) > 127:
                        value = value[:126]
                    
                    setattr(irf, field, value)
            
            if irf.verified_evidence_categorization == 'Should not count as an Intercept':
                irf.status = 'invalid'
            elif irf.verified_evidence_categorization is not None and irf.verified_evidence_categorization != '':
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
                        value = self.parse_date(value)
                    elif field not in long_fields and len(value) > 127:
                        value = value[:126]
                    
                    setattr(vdf, field, value)
            vdf.save()

    def process_cif_logbook(self, cif_class, row):
        column_field = {
            "Date CIF Received":"logbook_received",
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
                        value = self.parse_date(value)
                    elif field not in long_fields and len(value) > 127:
                        value = value[:126]
                    
                    setattr(cif, field, value)
            cif.save()
    
    def valid_date(self, the_date):
        if the_date is None or the_date == '':
            return False
        else:
            return True
    
    def fill_dates(self, irf_class, cif_class, vdf_class):
        for form_class in [irf_class, cif_class, vdf_class]:
            form_instances = form_class.objects.all()
            for form_instance in form_instances:
                modified = False
                if form_instance.status == 'in-progress':
                    continue
                if form_class == irf_class and (form_instance.evidence_categorization is None or form_instance.evidence_categorization == ''):
                    continue
                
                if form_class == irf_class and self.valid_date(form_instance.verified_date) and not self.valid_date(form_instance.logbook_first_verification_date):
                    form_instance.logbook_first_verification_date = form_instance.verified_date
                    modified = True
                
                if (form_class == irf_class and self.valid_date(form_instance.logbook_first_verification_date) 
                        and form_instance.verified_evidence_categorization != ''
                        and not self.valid_date(form_instance.verified_date)):
                    form_instance.verified_date = form_instance.logbook_first_verification_date
                    modified = True
                
                if not self.valid_date(form_instance.logbook_received):
                    form_instance.logbook_received = form_instance.date_time_entered_into_system
                    modified = True
                
                if not self.valid_date(form_instance.logbook_submitted):
                    if self.valid_date(form_instance.logbook_information_complete):
                        form_instance.logbook_submitted = form_instance.logbook_information_complete
                    else:
                        form_instance.logbook_submitted = form_instance.logbook_received
                    modified = True
                
                if not self.valid_date(form_instance.logbook_information_complete):
                    form_instance.logbook_information_complete = form_instance.logbook_received
                    modified = True
                
                if modified:
                    form_instance.save()

    def handle(self, *args, **options):
        in_file = options['in_file'][0]
        base_form = options['base_form_name'][0]
        if options['dateFormat']:
            self.date_formats = options['dateFormat']
        else:
            self.date_formats = ['%m/%d/%Y']
        
        forms = Form.objects.filter(form_name='irf' + base_form)
        if len(forms) == 1:
            irf_class = forms[0].storage.get_form_storage_class()
        else:
            print('Unable to find form irf' + base_form_name)
            return
        
        forms = Form.objects.filter(form_name='cif' + base_form)
        if len(forms) == 1:
            cif_class = forms[0].storage.get_form_storage_class()
        else:
            print('Unable to find form cif' + base_form_name)
            return
        
        forms = Form.objects.filter(form_name='vdf' + base_form)
        if len(forms) == 1:
            vdf_class = forms[0].storage.get_form_storage_class()
        else:
           print('Unable to find form vdf' + base_form_name)
           return
        
        
        with open(in_file) as csvfile:
            reader = csv.DictReader(csvfile)
            self.process_logbook(reader, irf_class, cif_class, vdf_class)
        
        
        self.fill_dates(irf_class, cif_class, vdf_class)
