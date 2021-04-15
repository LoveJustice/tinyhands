import csv
import json
import requests
import traceback
from datetime import date
from django.db import transaction, IntegrityError
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from dataentry.models import IrfCommon, IntercepteeCommon, LegalCase, LegalCaseSuspect, LegalCaseTimeline, LegalCaseVictim, MasterPerson, Person
from dataentry.models import BorderStation


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('in_file', nargs='+', type=str)
        parser.add_argument('status', nargs='+', type=str)
    
    def new_person (self, name):
        master = MasterPerson()
        master.full_name = name
        master.save()
        person = Person()
        person.full_name = name
        person.master_person = master
        person.master_set_notes = 'Import legal case'
        person.save()
        return person
    
    def parse_victims(self, victim_string):
        tmp = victim_string.replace(')',',').replace(';',',')
        items = tmp.split(',')
        victims = []
        for item in items:
            parts = item.split(' ')
            sep = ''
            name = ''
            for part in parts:
                tmp = part.strip()
                if tmp == '' or tmp.isnumeric():
                    continue
                name += sep + tmp
                sep = ' '
            
            if name == '':
                continue
            victims.append(name)
        
        return victims
            
    
    def add_victims(self, legal_case, interceptees, victims):
        for victim in victims:
            person = None
            for interceptee in interceptees:
                if interceptee.person.role == 'PVOT' and interceptee.person.full_name == victim:
                    person = interceptee.person
                    person.id = None
                    person.save()
                    break

            if person is None:
                person = self.new_person(victim)
            
            victim = LegalCaseVictim()
            victim.legal_case = legal_case
            victim.person = person
            victim.save()
                
    
    def add_suspect(self, legal_case, row, prefix, interceptees):
        
        imprisonment = {
                '1 month or less':{'years':0,'months':1,'days':0},
                '1 week or less':{'years':0,'months':0,'days':7},
                '1 year':{'years':1,'months':0,'days':0},
                '10 years':{'years':10,'months':0,'days':0},
                '11 years':{'years':11,'months':0,'days':0},
                '12 years':{'years':12,'months':0,'days':0},
                '15 years':{'years':15,'months':0,'days':0},
                '2 weeks or less':{'years':0,'months':0,'days':14},
                '2 months':{'years':0,'months':2,'days':0},
                '2 years':{'years':2,'months':0,'days':0},
                '20 years':{'years':20,'months':0,'days':0},
                '3 months':{'years':0,'months':3,'days':0},
                '3 weeks or less':{'years':0,'months':0,'days':21},
                '3 years':{'years':3,'months':0,'days':0},
                '35 days':{'years':0,'months':0,'days':35},
                '4 years':{'years':4,'months':0,'days':0},
                '5 years':{'years':5,'months':0,'days':0},
                '6 years':{'years':6,'months':0,'days':0},
                '7 months':{'years':0,'months':7,'days':0},
                '7 years':{'years':7,'months':0,'days':0},
                '8 months':{'years':0,'months':8,'days':0},
                '8 years':{'years':8,'months':0,'days':0},
            }
        tmp = row[prefix + ' Name']
        if tmp is None or tmp.strip() == '':
            return
        
        suspect = LegalCaseSuspect()
        suspect.legal_case = legal_case
        name =  row[prefix + ' Name']
        person = None
        for interceptee in interceptees:
            if interceptee.person.full_name == name:
                person = interceptee.person
                break
        
        if person is None:     
            person = self.new_person(row[prefix + ' Name'])
        
        person.id = None
        person.save()
        suspect.person = person
        tmp = row[prefix + ' Charge Sheet']
        if tmp is not None:
            tmp = tmp.lower().strip()
            if tmp.find('yes') >= 0:
                suspect.named_on_charge_sheet = 'Yes'
            elif tmp.find('no') == 0:
                suspect.named_on_charge_sheet = 'No'
        
        suspect.arrest_status = row[prefix + ' Arrested?']
        tmp = row[prefix + ' Arrest Date']
        if tmp != '':
            suspect.arrest_date = tmp
        suspect.verdict = row[prefix + ' Verdict']
        tmp = row[prefix + ' Date of Verdict']
        if tmp != '':
            suspect.verdict_date = tmp
        tmp = row[prefix + ' Fine Amount']
        if tmp != '':
            tmp = tmp.replace(',','')
            if tmp.isnumeric():
                suspect.fine_amount = tmp
        tmp = row[prefix + ' Imprisonment Period']
        if tmp in imprisonment:
            suspect.imprisonment_years = imprisonment[tmp]['years']
            suspect.imprisonment_months = imprisonment[tmp]['months']
            suspect.imprisonment_days = imprisonment[tmp]['days']
            suspect.imprisonment_total_days = suspect.imprisonment_years * 365 + suspect.imprisonment_months * 30 + suspect.imprisonment_days
        elif tmp != '':
            print('Unable to find Imprisonment Period', tmp)
        suspect.save()
    
    def add_legal_case(self, row, status):
        columns = [
                {
                    'name':'IRF#',
                    'field':'legal_case_number',
                },
                {
                    'name':'Police Case #',
                    'field':'police_case',
                },
                {
                    'name':'Court Case #',
                    'field':'court_case',
                },
                {
                    'name':'Charge Sheet Date',
                    'field':'charge_sheet_date',
                },
                {
                    'name':'Last Contacted?',
                    'field':'date_last_contacted',
                },
            ]
        
        
        legal_case = LegalCase()
        try:
            legal_case.station = BorderStation.objects.get(station_name=row['Station'].strip())
        except:
            print ('Unable to locate station', row['Station'])
            return
        legal_case.status = status
        tmp = row['Type of Case']
        legal_case.case_type = ''
        if tmp is not None:
            tmp = tmp.lower()
            legal_case.case_type = tmp
            if tmp.find('trafficking') >= 0:
                legal_case.case_type = 'human trafficking'
                legal_case.human_trafficking = True
            if tmp.find('rape') >= 0:
                if legal_case.human_trafficking == False:
                    legal_case.case_type = 'rape'
                else:
                    legal_case.specific_code_law = 'Human Trafficking & Rape'
            if tmp.find('public') >= 0:
                legal_case.case_type =  'public case'
                
        legal_case.source = 'Intercept'
            
        for column in columns:
            value = row[column['name']]
            field = column['field']
            if field is not None and value != '':
                setattr(legal_case, field, value)
        legal_case.save()
        
        comment = row['What is Next Step? / Case Comments']
        if comment is not None and comment != '':
            timeline = LegalCaseTimeline()
            timeline.legal_case = legal_case
            timeline.comment = comment
            timeline.comment_date = date.today()
            timeline.save()
        
        try:
            base_number = legal_case.legal_case_number
            for idx in range(len(legal_case.station.station_code), len(base_number)):
                if base_number[idx] < '0' or base_number[idx] > '9':
                    base_number = base_number[:idx]
                    break
            irf = IrfCommon.objects.get(irf_number=base_number)
            interceptees = IntercepteeCommon.objects.filter(interception_record=irf)
        except ObjectDoesNotExist:
            print ("could not find IRF for IRF number ", legal_case.legal_case_number)
            interceptees = []
        
        self.add_victims(legal_case, interceptees, self.parse_victims(row['Name of Victim(s)']))
        
        for suspect in ['S1','S2','S3','S4','S5','S6','S7','S8','S9','S10']:
            self.add_suspect(legal_case, row, suspect, interceptees)
        
    def legal_case(self, row, status):
        if row['IRF#'] != '':
            try:
                with transaction.atomic():
                    self.add_legal_case(row, status)
            except IntegrityError as err:
                print('IntegrityError', err)
    
    def set_address (self, person, address_string):
        if address_string.strip() == '':
            return
        request_addr = address_string
        address_notes = 'import victim information [' + address_string + ']'
        
        response = None      
        url = 'https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?f=json&singleLine='
        try:
            print(person.id, url+request_addr)
            response = requests.get(url+request_addr)
            jdata = json.loads(response.content)
            candidates = jdata['candidates']
            if len(candidates) > 0:
                best = candidates[0]
                person.address = best
                person.latitude = best['location']['y']
                person.longitude = best['location']['x']
                person.address_notes = 'converted-' + address_notes
            else:
                person.address_notes = 'Failed to convert-' + address_notes
            
            person.save()
            addr_set = True
        except:
             print ('Exception caught', traceback.format_exc())
             print ("request failed", response, 'id=', person.id)
    
    def victim_info(self, row):
        if row['LC#'] == '':
            return
        try:
            legal_case = LegalCase.objects.get(legal_case_number=row['LC#'])
        except ObjectDoesNotExist:
            print('Unable to find legal case for ', row['LC#'])
            return
        
        victims = LegalCaseVictim.objects.filter(legal_case=legal_case)
        name = row['Victim Name']
        victim = None
        for tmp_victim in victims:
            if name == tmp_victim.person.full_name:
                victim = tmp_victim
        
        if victim is None:
            victim = LegalCaseVictim()
            victim.legal_case = legal_case
            victim.person = self.new_person(name)
        
        if row['Phone #'] != '':
            victim.person.phone_contact = row['Phone #']
        self.set_address(victim.person, row['Current Location / Address'])
        victim.alternate_phone = row['Alternative Phone #']
        if row['Date of Last Contact'] != '':
            victim.last_contact_date = row['Date of Last Contact']
        if row['Date of Last Attempt'] != '':
            victim.last_attempted_contact_date = row['Date of Last Attempt']
        victim.victim_staus = row['Update / Status of Victim']
        
        victim.person.save()
        victim.save()
        
    def handle(self, *args, **options):
        in_file = options['in_file'][0]
        status = options['status'][0]
        
        with open(in_file) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if status in ['active','closed','inactive']:
                    self.legal_case(row, status)
                else:
                    self.victim_info(row)