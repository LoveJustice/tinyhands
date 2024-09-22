import csv
import io

from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction

from legal.models import LegalCharge, CourtCase, LegalChargeSuspect, LegalChargeSuspectCharge, LegalChargeVictim, LegalChargeTimeline
from dataentry.models import BorderStation, Incident, MasterPerson, Person, Suspect, SuspectInformation, VdfCommon

class Command(BaseCommand):
    name_map = {}
    def add_arguments(self, parser):
        parser.add_argument('map_file', nargs='+', type=str)
        parser.add_argument('in_file', nargs='+', type=str)
        
    def extract_date(self, date_string):
        result = None
        if date_string.strip() != '':
            for fmt in ['%d-%b-%Y','%d-%m-%Y','%Y-%m-%d']:
                try:
                    result = datetime.strptime(date_string, fmt)
                    break
                except:
                    pass
            
            if result is None:
                print ('Unable to parse date"' + date_string + '"')
            
        return result
    
    def get_incident(self, irf_number):
        incident = None
        incident_number = irf_number
        while len(incident_number) > 3:
            last = incident_number[len(incident_number)-1:]
            if last < '0' or last > '9':
                incident_number = incident_number[0:len(incident_number)-1]
            else:
                break
        incidents = Incident.objects.filter(incident_number=incident_number)
        if len(incidents) < 1:
            if True:
                 print('Unable to find incident_number', incident_number)
            else:
                print('Unable to find incident_number', incident_number, 'creating')
                station = BorderStation.objects.get(station_code=incident_number[0:3])
                incident = Incident()
                incident.incident_number = incident_number
                incident.station = station
                incident.incident_date = datetime.now()
                incident.save()
        elif len(incidents) > 1:
            print('Error: Multiple incidents with incident_number', incident_number)
            return False
        else:
            incident = incidents[0]
        
        return incident
    
    def map_name(self, incident, name, type):
        rv = None
        key = incident.incident_number + ':' + name + ':' + type
        if key in Command.name_map:
            tmp = Command.name_map[key]
            rv = {'create':tmp['create']}
            if tmp['replace'] != '':
                rv['replace'] = tmp['replace']
            else:
                rv['replace'] = name
        else:
            rv = {'replace':name, 'create':False}
        return rv
    
    def create_sf(self, incident, name):
        master_person = MasterPerson()
        master_person.full_name = name
        master_person.save()
        
        person = Person()
        person.full_name = name
        person.master_person = master_person
        person.save()
        
        info_person = Person()
        info_person.full_name = name
        info_person.master_person = master_person
        info_person.save()
        
        existing_suspects = Suspect.objects.filter(sf_number__startswith=incident.incident_number).order_by('-sf_number')
        next_suffix = None
        for existing_suspect in existing_suspects:
            if len(existing_suspect.sf_number) == len(incident.incident_number) + 1:
                suffix = existing_suspect.sf_number[-1:]
                if suffix >= 'A' and suffix <= 'Y':
                    next_suffix = chr(ord(suffix) + 1)
                    break
        if next_suffix is None:
            next_suffix = 'A'
        
        sf = Suspect()
        sf.status = 'approved'
        sf.station = incident.station
        sf.merged_person = person
        sf.sf_number = incident.incident_number + next_suffix
        sf.save()
        sf.incidents.add(incident)
        
        info = SuspectInformation()
        info.suspect = sf
        info.incident = incident
        info.person = info_person
        info.save()
        return sf
    
    def get_sf(self, incident, in_name):
        tmp = self.map_name(incident, in_name, 'Suspect')
        name = tmp['replace']
        should_create = tmp['create']
        sf = None
        sfs = Suspect.objects.filter(incidents=incident, suspectinformation__person__full_name__iexact=name)
        if len(sfs) < 1:
            if should_create:
                sf = self.create_sf(incident, name)
            else:
                sfs2 = Suspect.objects.filter(incidents=incident)
                candidates = ''
                for sf in sfs2:
                    if candidates != '':
                        candidates += ','
                    candidates += sf.merged_person.full_name + '[' + sf.sf_number + ']'
                        
                    
                print ('Unable to find SF for IRF#', incident.incident_number, 'name', name,':' + candidates)
                isSuccess = False
        else:
            sf = sfs[0]
        
        return sf
    
    def create_pvf(self, incident, name):
        master_person = MasterPerson()
        master_person.full_name = name
        master_person.save()
        
        person = Person()
        person.full_name = name
        person.master_person = master_person
        person.save()
        
        existing_pvfs = VdfCommon.objects.filter(vdf_number__startswith=incident.incident_number).order_by('-vdf_number')
        next_suffix = None
        for existing_pvf in existing_pvfs:
            if len(existing_pvf.vdf_number) == len(incident.incident_number) + 1:
                suffix = existing_pvf.vdf_number[-1:]
                if suffix >= 'A' and suffix <= 'Y':
                    next_suffix = chr(ord(suffix) + 1)
                    break
        if next_suffix is None:
            next_suffix = 'A'        
                
        pvf = VdfCommon()
        pvf.status = 'approved'
        pvf.station = incident.station
        pvf.victim = person
        pvf.vdf_number = incident.incident_number + next_suffix
        pvf.save()
    
    def get_pvf(self, incident, in_name):
        tmp = self.map_name(incident, in_name, 'PV')
        name = tmp['replace']
        should_create = tmp['create']
        pvf = None
        vdfs = VdfCommon.objects.filter(vdf_number__startswith=incident.incident_number)
        candidates = ''
        for vdf in vdfs:
            vdf_base = vdf.vdf_number
            for idx in range(len(vdf.station.station_code), len(vdf.vdf_number)):
                the_char = vdf.vdf_number[idx]
                if (the_char < '0' or the_char > '9') and the_char != '_':
                    vdf_base = vdf.vdf_number[:idx]
                    break
            if vdf_base != incident.incident_number:
                continue
            if candidates != '':
                candidates += ','
            candidates += vdf.victim.full_name + '[' + vdf.vdf_number + ']'
            if vdf.victim.full_name.lower().strip() == name.lower().strip():
                pvf = vdf
                break
        if pvf is None:
            if should_create:
                pvf = self.create_pvf(incident, name)
            else:
                print ('Unable to find PVF for Victim on IRF# ', incident.incident_number, 'name', name, ':' + candidates)
                
        
        return pvf
    
    def process_legal_case(self, row):
        isSuccess = True
        irf_number = row['IRF#']
        incident = self.get_incident(irf_number)
        if incident is None:
            return False
        
        still_open = False;
        
        legal_charge = LegalCharge()
        legal_charge.incident = incident
        legal_charge.legal_charge_number = incident.incident_number
        legal_charge.station = incident.station
        #legal_charge.source = 
        #legal_charge.location = 
        cs_date = self.extract_date(row["Date - CS"])
        if row["Date - CS"] != '':
            legal_charge.charge_sheet_date = cs_date
        legal_charge.police_case = row["Police Case #"]
        if row['Type of Case'] != 'Human Trafficking':
            legal_charge.human_trafficking = 'Yes'
        else:
            legal_charge.human_trafficking = 'No'
        legal_charge.case_summary = row['What is Next Step? / Case Comments']
        legal_charge.date_last_contacted =self.extract_date(row['Last Contacted?'])
        legal_charge.missing_data_count = 0
        legal_charge.save()
        
        timeline = LegalChargeTimeline()
        timeline.legal_charge =legal_charge
        timeline.court_case_sequence = 1
        timeline.comment_date = datetime.now()
        timeline.comment = 'Import from spreadsheet'
        timeline.added_by = 'Import tool'
        timeline.save()
    
        
        court_case = CourtCase()
        court_case.legal_charge = legal_charge
        court_case.sequence_number = 1
        court_case.court_case = row['Court Case #']
        #court_case.status = models.CharField(max_length=127, null=True)
        charges = []
        if row['Type of Case'] == 'Human Trafficking & Rape':
            court_case.charges = 'Human Trafficking;Sexual Assault'
            charges = ['Human Trafficking','Sexual Assault']
        elif row['Type of Case'] == 'Forced Labor':
            court_case.charges = 'Human Trafficking'
            charges = ['Human Trafficking']
        elif row['Type of Case'] == 'Rape':
            court_case.charges = 'Sexual Assault'
            charges = ['Sexual Assault']
        else:
            court_case.charges = row['Type of Case']
            charges = [row['Type of Case']]
        court_case.save()
            
        #court_case.specific_code_law = 
        
        for suspect_index in range(1,11):
            prefix = 'Suspect ' + str(suspect_index) + ' '
            if row[prefix + 'First & Last Name'] == '':
                continue
            sf = self.get_sf(incident, row[prefix + 'First & Last Name'])
            if sf is None:
                isSuccess = False
                continue
            
            suspect = LegalChargeSuspect()
            suspect.legal_charge = legal_charge
            suspect.court_cases = '1'
            suspect.sf = sf
            arrested = row[prefix + 'Arrested?']
            if arrested[0:3] == 'Yes':
                suspect.arrested = 'Yes'
                if arrested[0:10] == 'Yes - But ':
                    suspect.arrest_status = arrested[10:]
                else:
                    suspect.arrest_status = arrested[6:] 
            else:
                if arrested[0:2] == 'No':
                    suspect.arrested = 'No'
                suspect.arrest_status = None
            suspect.arrest_date = self.extract_date(row[prefix + 'Arrest Date'])
            suspect.named_on_charge_sheet = row[prefix + 'Named in CS?']
            #taken_into_custody = models.CharField(max_length=127, null=True)
            #charged_with_crime = models.CharField(max_length=127, null=True)
            suspect.save()
            
                
            for theCharge in charges:
                charge = LegalChargeSuspectCharge()
                charge.legal_charge = legal_charge
                charge.sf = sf
                charge.court_case_sequence = '1'
                charge.charge = theCharge
                verdict = row[prefix + 'Verdict?']
                if verdict != 'Conviction' and verdict != 'Acquittal':
                    still_open = True
                else:
                    charge.legal_status = 'Verdict';
                charge.verdict = verdict
                verdict_date = self.extract_date(row[prefix + 'Date of Verdict'])
            
                charge.verdict_date = verdict_date
                charge.verdict_submitted_date = None
                #charge.imprisonment_years =suspect.imprisonment_years
                #if suspect.imprisonment_total_days is not None:
                #    charge.imprisonment_days = suspect.imprisonment_total_days % 365
                #else:
                #    charge.imprisonment_days = suspect.imprisonment_days
                #charge.imprisonment_total_days = suspect.imprisonment_total_days
                #charge.fine_amount = suspect.fine_amount
                #charge.fine_currency = suspect.fine_currency
                charge.save()
        
        if row['Victims'] != '':
            for theVictim in row['Victims'].split(';'):
                pvf = self.get_pvf(incident, theVictim)
                
                if pvf is None:
                    isSuccess = False
                    continue
                
                victim = LegalChargeVictim()
                victim.legal_charge = legal_charge
                victim.pvf= pvf
                victim.court_cases = '1'
                victim.save()
        
        if still_open:
            legal_charge.status = 'active'
        else:
            legal_charge.status = 'closed'
        
        legal_charge.save()
                
        return isSuccess
    
    def processHeader(self, theLine):
        suspect = False
        suspect_count = 0
        fields = theLine.split(',')
        outline = ''
        sep = ''
        for field in fields:
                if field == 'First & Last Name':
                        suspect = True
                        suspect_count += 1
                if field == "Lawyer's Name & Phone #":
                        suspect = False
                if suspect and field != '':
                        outline += sep + '"Suspect ' + str(suspect_count) + ' ' + field + '"'
                else:
                        outline += sep + '"' + field + '"'
                sep = ','
        return outline

    def process_map(self, file_name):     
        with open(file_name) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                incident_number = row['IRF#'] 
                while len(incident_number) > 3:
                    last = incident_number[len(incident_number)-1:]
                    if last < '0' or last > '9':
                        incident_number = incident_number[0:len(incident_number)-1]
                    else:
                        break 
                Command.name_map[incident_number + ':' + row['Legal Case Name'] + ':' + row['Type']] = {'replace':row['Matching Name in SL'], 'create':row['Needs Form']}
        
    def handle(self, *args, **options):
        map_file = options['map_file'][0]
        in_file = options['in_file'][0]
        isSuccess = True
        
        self.process_map(map_file)
        
        # pre-process file to get the headers correct
        file = open(in_file, 'r')
        lines = file.readlines()
        csv_strings = []
        count = 0
        for line in lines:
            count += 1
            if count == 2:
                csv_strings.append(self.processHeader(line))
            elif count > 2:
                csv_strings.append(line)
            # else ignore top line
        
        
        
        reader = csv.DictReader(csv_strings)
        with transaction.atomic():
            for row in reader:
                rc = self.process_legal_case(row)
                #print('IRF#', row['IRF#'], rc)
                isSuccess = isSuccess and rc
            
            if not isSuccess:
                raise Exception('import of legal cases failed')
                pass
 