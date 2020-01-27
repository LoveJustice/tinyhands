import csv
import collections
import datetime
import re

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from dataentry.models import Address1, Address2, BorderStation, CifIndia, LocationBoxIndia, Person, PersonBoxIndia, TransporationIndia, VdfIndia
from _sqlite3 import Row

class Processing:
    @staticmethod
    def tbd(obj, field, row, processing, prefix=''):
        pass
    
    @staticmethod
    def no_processing(obj, field, row, processing, prefix=''):
        pass
    
    @staticmethod
    def set_constant(obj, field, row, processing, prefix=''):
        setattr(obj, field, processing['constant'])
    
    @staticmethod
    def copy_value(obj, field, row, processing, prefix=''):
        value = row[prefix + processing['source']]
        setattr(obj, field, value)
    
    @staticmethod
    def copy_value_match(obj, field, row, processing, prefix=''):
        value = row[prefix + processing['source']]
        if 'match' in processing:
            if 'source' in processing['match'] and 'constant' in processing['match']:
                if row[prefix + processing['match']['source']] == processing['match']['constant']:
                    setattr(obj, field, value)
    
    @staticmethod
    def copy_int(obj, field, row, processing, prefix=''):
        value = row[prefix + processing['source']]
        if value == '' or not str.isdigit(value):
            value = None
        setattr(obj, field, value)
    
    @staticmethod
    def copy_date(obj, field, row, processing, prefix=''):
        source_value = row[prefix + processing['source']]
        value = datetime.datetime.strptime(source_value, '%m/%d/%Y').date()
        setattr(obj, field, value)
    
    @staticmethod
    def parse_years(obj, field, row, processing, prefix=''):
        source_value = row[prefix + processing['source']] 
        p = re.compile(r'(?P<val>[0-9]+)[ ]+year[s]*')
        m = p.search(source_value)
        if m is not None:
            setattr(obj, field, m.groups('val')[0])
    
    @staticmethod
    def parse_months(obj, field, row, processing, prefix=''):
        source_value = row[prefix + processing['source']] 
        p = re.compile(r'(?P<val>[0-9]+)[ ]+month[s]*')
        m = p.search(source_value)
        if m is not None:
            setattr(obj, field, m.groups('val')[0])
        
    @staticmethod
    def parse_days(obj, field, row, processing, prefix=''):
        source_value = row[prefix + processing['source']] 
        p = re.compile(r'(?P<val>[0-9]+)[ ]+day[s]*')
        m = p.search(source_value)
        if m is not None:
            setattr(obj, field, m.groups('val')[0])
        
        
    @staticmethod
    def set_map(obj, field, row, processing, prefix=''):
        value = row[prefix + processing['source']]
        mapping = processing['map']
        if value in mapping:
            setattr(obj, field, mapping[value])
    
    @staticmethod
    def set_station(obj, field, row, processing, prefix=''):
        station_code = row['VIF Number'][:3]
        stations = BorderStation.objects.filter(station_code=station_code, operating_country__name='India')
        if len(stations) == 1:
            setattr(obj, field, stations[0].id)
            
    @staticmethod
    def get_or_create_address1(column, row):
        address1 = None
        value = row[column]
        if value != '':
            address1s = Address1.objects.filter(name=value)
            if len(address1s) > 0:
                address1 = address1s[0]
            if address1 is None:
                address1 = Address1()
                address1.name = value
                address1.save()
        
        return address1
    
    @staticmethod
    def get_or_create_address2(column, row, address1):
        address2 = None
        value = row[column]
        if value != '':
            try:
                address2 = Address2.objects.get(name=value, address1=address1)
            except ObjectDoesNotExist:
                address2 = Address2()
                address2.name = value
                address2.address1 = address1
                address2.save()
        
        return address2
    
    @staticmethod
    def set_address(obj, field, row, processing, prefix=''):
        address2_text = row[prefix + processing['address2_source']]

        address1 = Processing.get_or_create_address1(prefix + processing['address1_source'], row)
        if address1 is not None:
            address2 = Processing.get_or_create_address2(prefix + processing['address2_source'], row, address1)
            if address2 is not None:
                setattr(obj, field, address2.id)
    
    @staticmethod
    def set_person(obj, field, row, processing, prefix=''):
        mapping = processing['map']
        person = Person()
        found_data = False
        for attr in ['full_name', 'age', 'gender', 'phone_contact', 'nationality']:
            if attr in mapping:
                if mapping[attr] != '':
                    found_data = True
                    value = row[prefix + mapping[attr]]
                    if value == '' and attr == 'age':
                        value = None
                    if attr == 'gender':
                        value = value.upper()[:1]
                    setattr(person, attr, value)
            else:
                setattr(person. attr, None)

        if 'address1' in mapping:
            address1 = Processing.get_or_create_address1(prefix + mapping['address1'], row)
            if address1 is not None:
                found_data = True
                person.address1 = address1
            if 'address2' in mapping and address1 is not None:
                address2 = Processing.get_or_create_address2(prefix + mapping['address2'], row, address1)
                if address2 is not None:
                    found_data = True
                    person.address2 = address2
            else:
                person.address2 = None
        else:
            person.address1 = None
            person.address2 = None
        if found_data:
            person.save()
            setattr(obj, field, person.id)
        else:
            setattr(obj, field, None)
            
    @staticmethod
    def destination(obj, field, row, processing, prefix=''):
        dests = ["Delhi", "Bihar", "Mumbai", "Bangalore", "Pune", "Goa", "Kolkata", "Malaysia", "Singapore", "Thailand", "Qatar", "Kuwait", "Saudi Arabia", "Don't Know"]
        
        if row['2.3 Where were you going?'] != '':
            dest = row['2.3 Where were you going?'] + ' '
            if row['2.3 Where were you going?'] == 'India':
                if row['India'] in dests:
                    dest = row['India']
                else:
                    dest += row['India']
            elif row['Gulf/Other'] != '':
                if row['Gulf/Other'] in dests:
                    dest = row['Gulf/Other']
                else:
                    dest += row['Gulf/Other']
            setattr(obj, field, dest)
    
    @staticmethod
    def combine(obj, field, row, processing, prefix=''):
        value = ''
        for piece in processing['combine']:
            if row[prefix + piece['source']] != '':
                value += piece['format'].format(row[prefix + piece['source']])
                
        setattr(obj, field, value)       
        

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('in_file', nargs='+', type=str)
        
    cif_processing = {
        '_state':{'operation':Processing.no_processing},
        'border_cross_air':{'operation':Processing.no_processing},
        'border_cross_foot':{'operation':Processing.no_processing},
        'border_cross_night':{'operation':Processing.no_processing},
        'border_cross_off_road':{'operation':Processing.no_processing},
        'border_cross_vehicle':{'operation':Processing.no_processing},
        'broker_relation': {'operation':Processing.copy_value, 'source':"3.3 Broker's Relation to Victim"},
        'case_exploration_abused':{'operation':Processing.no_processing},
        'case_exploration_detained_against_will':{'operation':Processing.no_processing},
        'case_exploration_under_14_sent_job':{'operation':Processing.no_processing},
        'case_exploration_under_16_separated':{'operation':Processing.no_processing},
        'case_exploration_under_18_sexually_abused':{'operation':Processing.set_map, 'source':'4.11 Did any of these take place on the way?','map':{
            'Sexual Abuse':True
            }},
        'case_notes': {'operation':Processing.copy_value, 'source':'Case Notes'},
        'cif_number': {'operation':Processing.copy_value, 'source':'VIF Number'},
        'consent_for_fundraising':{'operation':Processing.no_processing},
        'date_time_entered_into_system':{'operation':Processing.no_processing},
        'date_time_last_updated':{'operation':Processing.no_processing},
        'date_visit_police_station':{'operation':Processing.no_processing},
        'delayed_waiting_for_other_traffickers':{'operation':Processing.no_processing},
        'education':{'operation':Processing.set_map, 'source':'1.17 Education Level ', 'map':{
            "Bachelor's":'University',
            'Grade 11-12 High School':'Secondary',
            'Grade 4-8':'Primary',
            'Grade 9-10':'Secondary',
            'Grade 9-10, Grade 11-12 High School':'Secondary',
            'Informal Only':'None/Illiterate',
            'None':'None/Illiterate',
            'Primary Only':'Primary'
            }},
        'expected_earning':{'operation':Processing.copy_value, 'source':"3.10 If going for a job, how much did the broker say you'd be earning per month (IC)?"},
        'expected_earning_currency':{'operation':Processing.set_constant, 'constant':'IC'},
        'expected_earning_pb':{'operation':Processing.no_processing},
        'exploitation_debt_bondage_exp':{'operation':Processing.no_processing},
        'exploitation_debt_bondage_lb':{'operation':Processing.no_processing},
        'exploitation_debt_bondage_occ':{'operation':Processing.no_processing},
        'exploitation_debt_bondage_pb':{'operation':Processing.no_processing},
        'exploitation_forced_labor_exp':{'operation':Processing.no_processing},
        'exploitation_forced_labor_lb':{'operation':Processing.no_processing},
        'exploitation_forced_labor_occ':{'operation':Processing.no_processing},
        'exploitation_forced_labor_pb':{'operation':Processing.no_processing},
        'exploitation_forced_prostitution_exp':{'operation':Processing.no_processing},
        'exploitation_forced_prostitution_lb':{'operation':Processing.no_processing},
        'exploitation_forced_prostitution_occ':{'operation':Processing.no_processing},
        'exploitation_forced_prostitution_pb':{'operation':Processing.no_processing},
        'exploitation_organ_removal_exp':{'operation':Processing.no_processing},
        'exploitation_organ_removal_lb':{'operation':Processing.no_processing},
        'exploitation_organ_removal_occ':{'operation':Processing.no_processing},
        'exploitation_organ_removal_pb':{'operation':Processing.no_processing},
        'exploitation_other_exp':{'operation':Processing.no_processing},
        'exploitation_other_lb':{'operation':Processing.no_processing},
        'exploitation_other_occ':{'operation':Processing.no_processing},
        'exploitation_other_pb':{'operation':Processing.no_processing},
        'exploitation_other_value':{'operation':Processing.no_processing},
        'exploitation_physical_abuse_exp':{'operation':Processing.no_processing},
        'exploitation_physical_abuse_lb':{'operation':Processing.no_processing},
        'exploitation_physical_abuse_occ':{'operation':Processing.no_processing},
        'exploitation_physical_abuse_pb':{'operation':Processing.no_processing},
        'exploitation_sexual_abuse_exp':{'operation':Processing.no_processing},
        'exploitation_sexual_abuse_lb':{'operation':Processing.no_processing},
        'exploitation_sexual_abuse_occ':{'operation':Processing.set_map, 'source':'4.11 Did any of these take place on the way?','map':{
            'Sexual Abuse':True
            }},
        'exploitation_sexual_abuse_pb':{'operation':Processing.no_processing},
        'form_entered_by_id':{'operation':Processing.no_processing},
        'guardian_name':{'operation':Processing.no_processing},
        'guardian_phone':{'operation':Processing.no_processing},
        'guardian_relationship':{'operation':Processing.no_processing},
        'how_recruited_at_school':{'operation':Processing.set_map, 'source':'3.5 How did you meet the broker?','map':{
            'College':True
            }},
        'how_recruited_at_work':{'operation':Processing.set_map, 'source':'3.5 How did you meet the broker?','map':{
            'At work':True
            }},
        'how_recruited_broker_approached':{'operation':Processing.set_map, 'source':'3.5 How did you meet the broker?','map':{
            'He approached me':True
            }},
        'how_recruited_broker_approached_pb':{'operation':Processing.no_processing},
        'how_recruited_broker_called_pv':{'operation':Processing.set_map, 'source':'3.5 How did you meet the broker?','map':{
            'Called my mobile':True
            }},
        'how_recruited_broker_online':{'operation':Processing.set_map, 'source':'3.5 How did you meet the broker?','map':{
            'Facebook':True
            }},
        'how_recruited_broker_online_pb':{'operation':Processing.no_processing},
        'how_recruited_broker_other':{'operation':Processing.set_map, 'source':'3.5 How did you meet the broker?','map':{
            'At home':'At home',
            'At wedding':'At wedding',
            'At wedding':'At wedding',
            'Broker is from my community':'Broker is from my community',
            'In a hospital':'In a hospital',
            'In a vehicle':'In a vehicle',
            'Neighbor':'Neighbor',
            'Went to him myself':'Went to him myself'
            }},
        'how_recruited_broker_through_family':{'operation':Processing.set_map, 'source':'3.5 How did you meet the broker?','map':{
            'Through family':True,
            'He approached me, Through family':True,
            }},
        'how_recruited_broker_through_friends':{'operation':Processing.set_map, 'source':'3.5 How did you meet the broker?','map':{
            'Through friends':True,
            'Through friends, In buspark':True
            }},
        'how_recruited_job_ad':{'operation':Processing.no_processing},
        'how_recruited_married':{'operation':Processing.set_map, 'source':"3.3 Broker's Relation to Victim", 'map':{
            "Husband":True,
            }},
        'how_recruited_promised_job':{'operation':Processing.no_processing},
        'how_recruited_promised_marriage':{'operation':Processing.no_processing},
        'id':{'operation':Processing.no_processing},
        'id_kept_by_broker':{'operation':Processing.copy_value, 'source':'4.10 Is your passport or work permit with a broker?'},
        'id_made_fake':{'operation':Processing.no_processing},
        'id_made_false_name':{'operation':Processing.no_processing},
        'id_made_no':{'operation':Processing.set_map, 'source':'4.9 Was a passport made for you?','map':{
            'No':True,
            }},
        'id_made_other_false':{'operation':Processing.no_processing},
        'id_made_real':{'operation':Processing.set_map, 'source':'4.9 Was a passport made for you?','map':{
            'Real Passport':True,
            }},
        'id_source_pb':{'operation':Processing.no_processing},
        'incident_date':{'operation':Processing.no_processing},
        'informant_number':{'operation':Processing.no_processing},
        'interview_date': {'operation':Processing.copy_date, 'source':'Date'},
        'known_broker_days':{'operation':Processing.no_processing},
        'known_broker_months':{'operation':Processing.no_processing},
        'known_broker_pb':{'operation':Processing.no_processing},
        'known_broker_years':{'operation':Processing.no_processing},
        'legal_action_taken':{'operation':Processing.set_map, 'source':'8.1 Has legal action been taken against any of the traffickers?','map':{
            'Yes':'Yes, case filed',
            'No':'No',
            }},
        'legal_action_taken_case_type':{'operation':Processing.set_map, 'source':'8.1 Has legal action been taken against any of the traffickers?','map':{
            'Yes':'FIR',
            }},
        'legal_action_taken_filed_against':{'operation':Processing.copy_value, 'source':'FIR filed against:'},
        'legal_action_taken_staff_family_not_willing':{'operation':Processing.set_map, 'source':"8.2 If no, what's the main reason?",'map':{
            'Family afraid for her safety':True,
            'Family afraid of reputation':True,
            }},
        'legal_action_taken_staff_police_not_enough_info':{'operation':Processing.set_map, 'source':"8.2 If no, what's the main reason?",'map':{
            'Police say not enough information':True,
            }},
        'legal_action_taken_staff_pv_afraid_reputation':{'operation':Processing.set_map, 'source':"8.2 If no, what's the main reason?",'map':{
            'Victim afraid of reputation':True,
            }},
        'legal_action_taken_staff_pv_afraid_safety':{'operation':Processing.set_map, 'source':"8.2 If no, what's the main reason?",'map':{
            'Victim afraid for her safety':True,
            }},
        'legal_action_taken_staff_pv_does_not_believe':{'operation':Processing.no_processing},
        'legal_action_taken_staff_pv_or_family_bribed':{'operation':Processing.no_processing},
        'legal_action_taken_staff_pv_threatened':{'operation':Processing.no_processing},
        'legal_action_taken_staff_trafficker_ran':{'operation':Processing.set_map, 'source':"8.2 If no, what's the main reason?",'map':{
            "Trafficker is victim's own people":True,
            'She was going herself, Trafficker ran away':True,
            "Trafficker is victim's own people, Trafficker ran away":True
            }},
        'legal_action_taken_staff_trafficker_relative':{'operation':Processing.set_map, 'source':"8.2 If no, what's the main reason?",'map':{
            'Trafficker ran away':True,
            "Trafficker is victim's own people, Trafficker ran away":True
            }},
        'location':{'operation':Processing.no_processing},
        'logbook_incomplete_questions':{'operation':Processing.no_processing},
        'logbook_incomplete_sections':{'operation':Processing.no_processing},
        'logbook_information_complete':{'operation':Processing.no_processing},
        'logbook_notes':{'operation':Processing.no_processing},
        'logbook_received':{'operation':Processing.no_processing},
        'logbook_submitted':{'operation':Processing.no_processing},
        'main_pv_id':{'operation':Processing.set_person, 'map':{
            'full_name':'1.1 Victim Name',
            'age':'1.4 Victim Age',
            'gender':'1.2 Victim Gender',
            'phone_contact':'Victim Phone Number',
            'address1':'Victim District/State',
            'address2':'Victim VDC/Village/Police Station',
            'nationality':'1.7 Nationality'}},
        'married_broker_days':{'operation':Processing.parse_days, 'source':'3.4 If married to the broker, how long have you been married? (number and then clarify if it is months or years)'},
        'married_broker_months':{'operation':Processing.parse_months, 'source':'3.4 If married to the broker, how long have you been married? (number and then clarify if it is months or years)'},
        'married_broker_pb':{'operation':Processing.no_processing},
        'married_broker_years':{'operation':Processing.parse_years, 'source':'3.4 If married to the broker, how long have you been married? (number and then clarify if it is months or years)'},
        'number_of_traffickers':{'operation':Processing.copy_int, 'source':'# of Traffickers'},
        'number_of_victims':{'operation':Processing.copy_int, 'source':'# of Victims'},
        'occupation':{'operation':Processing.copy_value, 'source':'1.10 What is your occupation?'},
        'officer_name':{'operation':Processing.no_processing},
        'other_possible_victims':{'operation':Processing.no_processing},
        'permission_contact_facebook':{'operation':Processing.no_processing},
        'permission_contact_phone':{'operation':Processing.no_processing},
        'permission_contact_pv':{'operation':Processing.no_processing},
        'permission_contact_whats_app':{'operation':Processing.no_processing},
        'planned_destination':{'operation':Processing.destination},
        'police_are_scared':{'operation':Processing.no_processing},
        'police_do_not_believe_crime':{'operation':Processing.no_processing},
        'police_interact_disrespectful':{'operation':Processing.no_processing},
        'police_interact_none':{'operation':Processing.no_processing},
        'police_interact_resistant_to_fir':{'operation':Processing.no_processing},
        'police_interact_unprofessional':{'operation':Processing.no_processing},
        'police_say_not_enough_evidence':{'operation':Processing.set_map, 'source':"8.2 If no, what's the main reason?",'map':{
            'Police say not enough information':True,
            }},
        'police_station_gave_trafficker_access_to_pv':{'operation':Processing.no_processing},
        'police_station_threats_prevented_statement':{'operation':Processing.no_processing},
        'police_station_took_statement':{'operation':Processing.no_processing},
        'police_station_took_statement_privately':{'operation':Processing.no_processing},
        'police_station_victim_name_given_to_media':{'operation':Processing.no_processing},
        'purpose_for_leaving_education':{'operation':Processing.set_map, 'source':"2.1 What was the main purpose for which you left home?",'map':{
            'Education':True,
            }},
        'purpose_for_leaving_family':{'operation':Processing.set_map, 'source':"2.1 What was the main purpose for which you left home?",'map':{
            'To meet relative':True,
            'Meet your own family':True,
            }},
        'purpose_for_leaving_job_hotel':{'operation':Processing.set_map, 'source':"2.1 What was the main purpose for which you left home?",'map':{
            'Job - Hotel':True,
            'Job - Hotel, Dance': True,
            'Job - Hotel, Dance Bar':True,
            }},
        'purpose_for_leaving_job_household':{'operation':Processing.set_map, 'source':"2.1 What was the main purpose for which you left home?",'map':{
            'Job - Household':True,
            }},
        'purpose_for_leaving_marriage':{'operation':Processing.set_map, 'source':"2.1 What was the main purpose for which you left home?",'map':{
            'Marriage':True,
            }},
        'purpose_for_leaving_medical':{'operation':Processing.set_map, 'source':"2.1 What was the main purpose for which you left home?",'map':{
            'Medical Treatment':True,
            }},
        'purpose_for_leaving_other':{'operation':Processing.set_map, 'source':"2.1 What was the main purpose for which you left home?",'map':{
            'Arranged Marriage':'Arranged Marriage',
            'Catering':'Catering',
            'Cathering':'Cathering',
            'Child Labour':'Child Labour',
            'Club Dancer':'Club Dancer',
            'Dance Bar':'Dance Bar',
            'Discussion':'Discussion',
            'Domestic and child labor':'Domestic and child labor',
            "don't know details":"don't know details",
            "Don't want to go school":"Don't want to go school",
            "Don't want to study":"Don't want to study",
            "Eloping":"Eloping",
            "Having family problem":"Having family problem",
            "Job - Baby Care":"Job - Baby Care",
            "Job - Broker did not say what job":"Job - Broker did not say what job",
            "Job - Factory":"Job - Factory",
            "Job - Hotel, Dance":"Dance",
            "Job - Hotel, Dance Bar":"Dance Bar",
            "Job - Laborer":"Job - Laborer",
            "Job - Other":"Job - Other",
            "Job - Shop":"Job - Shop",
            "Looking for a job":"Looking for a job",
            "Looking for ajob":"Looking for a job",
            "Marketing":"Marketing",
            "Not good enviroment":"Not good enviroment",
            "Ran away from home":"Ran away from home",
            "Ranaway":"Ranaway",
            "Run away":"Run away",
            "Run away from home":"Run away from home",
            "Runaway":"Runaway",
            "To meet the unknown person":"To meet the unknown person",
            "Visit broker's home":"Visit broker's home"
            }},
        'purpose_for_leaving_travel_tour':{'operation':Processing.set_map, 'source':"2.1 What was the main purpose for which you left home?",'map':{
            'Travel/Tour':True,
            }},
        'pv_signed_form':{'operation':Processing.set_map, 'source':"Signature is on the original form?",'map':{
            'Signature is on the original form':True,
            }},
        'pv_think_would_have_been_trafficked':{'operation':Processing.set_map, 'source':"6.2 Do you think you would've been trafficked if you hadn't been intercepted by Tiny Hands?",'map':{
            "Doesn't Know":"Doesn't know",
            "No, blames TH for stopping her":"No",
            "Yes, thankful to TH for saving her":"Yes",
            "Yes, thankful to TH for saving her, Doesn't Know":"Yes",
            }},
        'pv_will_not_testify':{'operation':Processing.no_processing},
        'recruited_agency':{'operation':Processing.set_map, 'source':"3.1 Was a manpower involved?",'map':{
            'Yes':True,
            }},
        'recruited_agency_pb':{'operation':Processing.no_processing},
        'recruited_broker':{'operation':Processing.set_map, 'source':"3.2 Did someone recruit you in your village/persuade you to go abroad?",'map':{
            'Yes':True,
            }},
        'recruited_broker_pb':{'operation':Processing.no_processing},
        'recruited_no':{'operation':Processing.set_map, 'source':"3.2 Did someone recruit you in your village/persuade you to go abroad?",'map':{
            'No (skip the rest of this section)':True,
            }},
        'reported_blue_flags':{'operation':Processing.copy_int, 'source':"Total Home Situational Alarms"},
        'social_media':{'operation':Processing.no_processing},
        'source_of_intelligence':{'operation':Processing.set_constant, 'constant':'Intercept'},
        'staff_name':{'operation':Processing.copy_value, 'source':'Interviewer'},
        'station_id':{'operation':Processing.set_station},
        'status':{'operation':Processing.set_constant, 'constant':'approved'},
        'suspect_corruption_or_bribes':{'operation':Processing.set_map, 'source':"3.2 Did someone recruit you in your village/persuade you to go abroad?",'map':{
            'Interference by powerful people':True,
            }},
        'suspected_trafficker_count':{'operation':Processing.no_processing},
        'total_blue_flags':{'operation':Processing.copy_int, 'source':"Total Home Situational Alarms"},
        'trafficker_ran_away':{'operation':Processing.set_map, 'source':"8.2 If no, what's the main reason?",'map':{
            "Trafficker ran away":True,
            "Trafficker is victim's own people, Trafficker ran away":True,
            }},
        'travel_expenses_broker_repaid_amount':{'operation':Processing.copy_value_match, 'source':"Amount paid broker", "match":{
                "source":"3.8 How was the expense paid for taking you to the destination paid for?",
                "constant":"the broker paid the expenses and I have to pay him back",
            }},
        'travel_expenses_paid_by_broker':{'operation':Processing.set_map, 'source':"3.8 How was the expense paid for taking you to the destination paid for?",'map':{
            "the broker paid all the expenses":True,
            }},
        'travel_expenses_paid_by_broker_pb':{'operation':Processing.no_processing},
        'travel_expenses_paid_by_broker_repaid':{'operation':Processing.set_map, 'source':"3.8 How was the expense paid for taking you to the destination paid for?",'map':{
            "the broker paid the expenses and I have to pay him back":True,
            }},
        'travel_expenses_paid_by_broker_repaid_pb':{'operation':Processing.no_processing},
        'travel_expenses_paid_themselves':{'operation':Processing.set_map, 'source':"3.8 How was the expense paid for taking you to the destination paid for?",'map':{
            "I paid the expenses myself":True,
            }},
        'travel_expenses_paid_to_broker':{'operation':Processing.set_map, 'source':"3.8 How was the expense paid for taking you to the destination paid for?",'map':{
            "I gave a sum of money to the broker":True,
            }},
        'travel_expenses_paid_to_broker_amount':{'operation':Processing.copy_value_match, 'source':"Amount paid broker", "match":{
                "source":"3.8 How was the expense paid for taking you to the destination paid for?",
                "constant":"I gave a sum of money to the broker",
            }},
        'travel_expenses_paid_to_broker_pb':{'operation':Processing.no_processing},
        'unable_to_locate_trafficker':{'operation':Processing.no_processing},
        'victim_statement_certified':{'operation':Processing.no_processing},
        'victim_statement_certified_date':{'operation':Processing.no_processing},
        }
        
    pb_processing = {
        '_state':{'operation':Processing.no_processing},
        'appearance':{'operation':Processing.combine, 'combine':[
            {'source':'Appearance', 'format':'{}'},
            {'source':'Height (ft)', 'format':',Height {}'},
            {'source':'Weight (kg)', 'format':',Weight {}'},
            ]},
        'arrested':{'operation':Processing.no_processing},
        'associated_lb':{'operation':Processing.copy_value, 'source':"If yes, LB#"},
        'case_filed_against':{'operation':Processing.no_processing},
        'cif_id':{'operation':Processing.no_processing},
        'definitely_trafficked_many':{'operation':Processing.set_map, 'source':"What do you believe about him? - Interviewer",'map':{
            "Definitely trafficked many girls":True,
            }},
        'dont_believe_trafficker':{'operation':Processing.set_map, 'source':"What do you believe about him? - Interviewer",'map':{
            "Don't believe he's a trafficker":True,
            }},
        'flag_count':{'operation':Processing.no_processing},
        'has_trafficked_some':{'operation':Processing.set_map, 'source':"What do you believe about him? - Interviewer",'map':{
            "Has trafficked some girls":True,
            }},
        'id':{'operation':Processing.no_processing},
        "occupation":{'operation':Processing.copy_value, 'source':"Occupation"},
        'pb_number':{'operation':Processing.no_processing},
        'person_id':{'operation':Processing.set_person, 'map':{
            'full_name':'Name',
            'age':'Age',
            'gender':'Gender',
            'phone_contact':'Phone #',
            'address1':'District/State',
            'address2':'VDC/Village',
            'nationality':'Nationality'
            }},
        'pv_definitely_trafficked_many':{'operation':Processing.set_map, 'source':"What do you believe about him - Victim",'map':{
            "Definitely trafficked many girls":True,
            }},
        'pv_dont_believe_trafficker':{'operation':Processing.set_map, 'source':"What do you believe about him - Victim",'map':{
            "Don't believe he's a trafficker":True,
            }},
        'pv_has_trafficked_some':{'operation':Processing.no_processing},
        'pv_suspected_trafficker':{'operation':Processing.set_map, 'source':"What do you believe about him - Victim",'map':{
            "Suspect he's a trafficker":True,
            }},
        'relation_to_pv':{'operation':Processing.no_processing},
        'role_agent':{'operation':Processing.no_processing},
        'role_broker':{'operation':Processing.set_map, 'source':"Who is this? Pt. 2",'map':{
            "Broker":True,
            }},
        'role_companion':{'operation':Processing.set_map, 'source':"Who is this? Pt. 2",'map':{
            "Companion":True,
            }},
        'role_complainant':{'operation':Processing.no_processing},
        'role_host':{'operation':Processing.no_processing},
        'role_id_facilitator':{'operation':Processing.no_processing},
        'role_other':{'operation':Processing.set_map, 'source':"Who is this? Pt. 2",'map':{
            "India Trafficker":"India Trafficker",
            }},
        'role_witness':{'operation':Processing.no_processing},
        'social_media':{'operation':Processing.no_processing},
        'suspected_trafficker':{'operation':Processing.set_map, 'source':"What do you believe about him? - Interviewer",'map':{
            "Suspect he's a trafficker":True,
            }},
        }
    
    lb_processing = {
        '_state':{'operation':Processing.no_processing},
        'address2_id':{'operation':Processing.set_address, "address1_source":"District/State", "address2_source":"VDC/Village"},
        'associated_pb':{'operation':Processing.copy_value, 'source':"If yes, PB#"},
        'cif_id':{'operation':Processing.no_processing},
        'color':{'operation':Processing.copy_value, 'source':"Color"},
        'country':{'operation':Processing.copy_value, 'source':"Which country?"},
        'flag_count':{'operation':Processing.no_processing},
        'id':{'operation':Processing.no_processing},
        'lb_number':{'operation':Processing.no_processing},
        'location_in_town':{'operation':Processing.copy_value, 'source':"Location in Town"},
        'name_signboard':{'operation':Processing.copy_value, 'source':"Nearby Signboard"},
        'nearby_landmarks':{'operation':Processing.copy_value, 'source':"Nearby landmarks"},
        'number_of_levels':{'operation':Processing.copy_value, 'source':"# of levels"},
        'number_other_pvs_at_location':{'operation':Processing.no_processing},
        'person_in_charge':{'operation':Processing.copy_value, 'source':"Person in charge"},
        'phone':{'operation':Processing.copy_value, 'source':"Phone #"},
        'place':{'operation':Processing.copy_value, 'source':"Which place?"},
        'place_kind':{'operation':Processing.copy_value, 'source':"What kind of place is it?"},
        'pv_attempt_hide_explaination':{'operation':Processing.no_processing},
        'pv_attempt_hide_no':{'operation':Processing.no_processing},
        'pv_attempt_hide_not_applicable':{'operation':Processing.no_processing},
        'pv_attempt_hide_yes':{'operation':Processing.no_processing},
        'pv_free_to_go_explaination':{'operation':Processing.no_processing},
        'pv_free_to_go_no':{'operation':Processing.no_processing},
        'pv_free_to_go_not_applicable':{'operation':Processing.no_processing},
        'pv_free_to_go_yes':{'operation':Processing.no_processing},
        'pv_stayed_days':{'operation':Processing.no_processing},
        'pv_stayed_not_applicable':{'operation':Processing.no_processing},
        'pv_stayed_start_date':{'operation':Processing.no_processing},
        }
    
    vdf_processing = {
        '_state':{'operation':Processing.no_processing},
        'awareness_of_exploitation_before_interception':{'operation':Processing.set_map, 'source':"6.1 Before you were intercepted, were you aware that girls going abroad are often deceived and end up in very exploitative situations?",'map':{
            "Had heard, but never knew how bad it was until I was intercepted":"Had heard, but never knew how bad it was until I was intercepted by TH/LJ",
            "Had heard, but never knew how bad it was until I was intercepted, Knew how bad it was, but didn't think that was happening to her":"Knew how bad it was, but didn't think it was happening to them",
            "Had never heard about it":"Had never heard about it",
            "Knew how bad it was, but didn't think that was happening to her":"Knew how bad it was, but didn't think it was happening to them",
            }},
        'case_notes': {'operation':Processing.copy_value, 'source':'Case Notes'},
        'consent_to_use_information':{'operation':Processing.no_processing},
        'date_time_entered_into_system':{'operation':Processing.no_processing},
        'date_time_last_updated':{'operation':Processing.no_processing},
        'date_victim_left':{'operation':Processing.no_processing},
        'do_you_want_to_go_home':{'operation':Processing.copy_value, 'source':"7.5 Do you want to go home?"},
        'emotional_abuse':{'operation':Processing.set_map, 'source':"Emotional Abuse",'map':{
            "Frequently/Severe":"Frequent/Severe",
            "No":"Never",
            "Rarely/Minor":"Rarely/Minor",
            }},
        'express_suicidal_thoughts':{'operation':Processing.copy_value, 'source':"7.10 Did she express suicidal thoughts at any point?"},
        'family_economic_situation':{'operation':Processing.set_map, 'source':"7.9 Economic Situation of Family",'map':{
            "Able to meet basic needs, but difficult":"Able to meet only basic needs, but it is very difficult",
            "Comfortably meets basic needs":"Comfortably meet basic needs, and can afford to buy some non-essential goods/services",
            "Unable to Meet Basic Needs":"Unable to meet basic needs",
            "Wealthy":"Wealthy",
            }},
        'family_guardian_pressure':{'operation':Processing.copy_value, 'source':"7.2 Did your family/guardian pressure you in any way to accept the broker's offer?"},
        'feel_safe_with_guardian':{'operation':Processing.copy_value, 'source':"7.4 Do you feel safe at home with your guardian?"},
        'form_entered_by_id':{'operation':Processing.no_processing},
        'fundraising_purpose':{'operation':Processing.set_map, 'source':"Permission to use photograph?",'map':{
            "Check the box if this question on form is signed":"I give permission to use my story and photograph anywhere",
            }},
        'guardian_drink_alcohol':{'operation':Processing.set_map, 'source':"7.7 Does the guardian drink alcohol?",'map':{
            "Constnatly":"Frequent/Severe",
            "Never":"Never",
            "Occasional":"Rarely/Minor",
            }},
        'guardian_know_destination':{'operation':Processing.copy_value, 'source':"7.1 Did you guardian know you were travelling to India"},
        'guardian_name':{'operation':Processing.no_processing},
        'guardian_phone':{'operation':Processing.no_processing},
        'guardian_signature':{'operation':Processing.no_processing},
        'guardian_use_drugs':{'operation':Processing.set_map, 'source':"7.8 Does the guardian use drugs?",'map':{
            "All the time":"All the Time",
            "Never":"Never",
            "Occasional":"Occasionally",
            }},
        'id':{'operation':Processing.no_processing},
        'interview_date': {'operation':Processing.copy_date, 'source':'Date'},
        'location':{'operation':Processing.no_processing},
        'logbook_incomplete_questions':{'operation':Processing.no_processing},
        'logbook_incomplete_sections':{'operation':Processing.no_processing},
        'logbook_information_complete':{'operation':Processing.no_processing},
        'logbook_notes':{'operation':Processing.no_processing},
        'logbook_received':{'operation':Processing.no_processing},
        'logbook_submitted':{'operation':Processing.no_processing},
        'occupation':{'operation':Processing.copy_value, 'source':'1.10 What is your occupation?'},
        'physical_abuse':{'operation':Processing.set_map, 'source':"Physical Abuse",'map':{
            "Frequently/Severe":"Frequently/Severe",
            "No":"Never",
            "Rarely/Minor":"Rarely/Minor",
            }},
        'sexual_abuse':{'operation':Processing.set_map, 'source':"7.6 Is the victim subject to any of these by someone in her home? - Sexual Abuse",'map':{
            "Frequently/Severe":"Frequently/Severe",
            "No":"Never",
            "Rarely/Minor":"Rarely/Minor",
            }},
        'share_gospel_book':{'operation':Processing.no_processing},
        'share_gospel_film':{'operation':Processing.no_processing},
        'share_gospel_oral':{'operation':Processing.no_processing},
        'share_gospel_other':{'operation':Processing.no_processing},
        'share_gospel_testimony':{'operation':Processing.no_processing},
        'share_gospel_tract':{'operation':Processing.no_processing},
        'shelter_accomodation':{'operation':Processing.copy_int, 'source':'Shelter Accommodations'},
        'shelter_staff_polite':{'operation':Processing.copy_int, 'source':'Shelter staff polite and respectful'},
        'someone_pick_up_victim':{'operation':Processing.no_processing},
        'staff_name':{'operation':Processing.copy_value, 'source':'Interviewer'},
        'staff_share_gospel':{'operation':Processing.no_processing},
        'station_id':{'operation':Processing.set_station},
        'station_recommendation_for_victim':{'operation':Processing.set_map, 'source':"8.3 What is your recommendation about where she should go?",'map':{
            "Plan to send the girl home to stay with her guardians":" Send victim home to stay with guardians",
            "Plan to Send the girl to stay with other relatives":"Send the victim to stay with other relatives",
            "Tiny Hands needs to help her find another place to go":" TH/LJ needs to help them find another place to go",
            }},
        'status':{'operation':Processing.set_constant, 'constant':'approved'},
        'total_situational_alarms':{'operation':Processing.copy_int, 'source':'Total Home Situational Alarms'},
        'trafficking_awareness':{'operation':Processing.copy_int, 'source':'Trafficking Awareness'},
        'transit_staff_polite':{'operation':Processing.copy_int, 'source':'6.5 How would you rate the work othat Tiny Hands is doing on a scared of 1-10 in each area: Monitors are polite and respectful'},
        'try_to_send_overseas_again':{'operation':Processing.copy_value, 'source':'7.3 If they attempted to send you abroad, do you think they will try to send you again?'},
        'vdf_number': {'operation':Processing.copy_value, 'source':'VIF Number'},
        'victim_heard_message_before':{'operation':Processing.set_map, 'source':"6.3 Had you heard about the gospel of Jesus before coming to TH?",'map':{
            "Had heard the gospel but never believed":"Yes - heard but didn't believe",
            "Has heard the name only":"No",
            "Has heard the name only, Had heard the gospel but never believed":"Yes - heard but didn't believe",
            "No, I have never heard":"No",
            "Was already a believer":"Yes - heard and was believer",
            }},
        "victim_id":{'operation':Processing.set_person, 'map':{
            'full_name':'1.1 Victim Name',
            'age':'1.4 Victim Age',
            'gender':'1.2 Victim Gender',
            'phone_contact':'Victim Phone Number',
            'address1':'Victim District/State',
            'address2':'Victim VDC/Village/Police Station',
            'nationality':'1.7 Nationality'}},
        'victim_signature':{'operation':Processing.set_map, 'source':"Signature is on the original form?",'map':{
            "Signature is on the original form":True,
            }},
        'what_victim_believes_now':{'operation':Processing.set_map, 'source':"6.4 If she wasn't already a believer, what does she believe now?",'map':{
            "Believes in Jesus and plans to go to church":"Do believe and plan on going to center",
            "Believes in Jesus, but doesn't plan to go to church":"Do believe, but don't plan on going to center",
            "Doesn't believe in Jesus":"Don't believe",
            }},
        'where_victim_sent':{'operation':Processing.no_processing},
        'who_victim_released':{'operation':Processing.no_processing},
        'who_victim_released_name':{'operation':Processing.no_processing},
        'who_victim_released_phone':{'operation':Processing.no_processing},
        }
    
    
    def handle(self, *args, **options):
        self.new_cifs = 0
        self.existing_cifs = 0
        self.new_vdfs = 0
        self.existing_vdfs = 0
        self.missing_data = False
        in_file = options['in_file'][0]
        with open(in_file) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.process_cif(row)
                self.process_vdf(row)
                if self.missing_data:
                    break
    
    def process_cif(self, row):
        cif_number = row['VIF Number']
        cifs = CifIndia.objects.filter(cif_number=cif_number)
        if len(cifs) > 0:
            self.existing_cifs += 1
            return
        
        cif = CifIndia()
        ordered_attrs = sorted(cif.__dict__.keys())
        for attr in ordered_attrs:
            if attr not in Command.cif_processing:
                print('Unable to find processing rule for CIF field ', attr)
                self.missing_data = True
                continue
            
            processing = Command.cif_processing[attr]
            processing['operation'](cif, attr, row, processing)
        
        cif.save()
        
        self.process_transportation(row, cif)
        self.process_person_boxes(row, cif)
        self.process_location_boxes(row, cif)
        
    def process_person_boxes(self, row, cif):
        index = 0
        for idx in range(1,3):
            prefix = 'PB' + str(idx) + ' '
            if row[prefix + 'Name'] == '' and row[prefix + 'Gender'] == '' and row[prefix + 'Age'] == '':
                continue     
            
            index += 1
            pb = PersonBoxIndia()
            ordered_attrs = sorted(pb.__dict__.keys())
            for attr in ordered_attrs:
                if attr not in Command.pb_processing:
                    print('Unable to find processing rule for PB field ', attr)
                    self.missing_data = True
                    continue
            
                processing = Command.pb_processing[attr]
                processing['operation'](pb, attr, row, processing, prefix=prefix)
            
            if pb.person is None:
                print (cif.cif_number, row[prefix + 'Name'], row[prefix + 'Gender'], row[prefix + 'Age'])
            
            pb.cif = cif
            pb.pb_number = index
            pb.save()
    
    def process_location_boxes(self, row, cif):
        index = 0
        for idx in range(1,3):
            prefix = 'LB' + str(idx) + ' '
            if row[prefix + 'Which place?'] == '' and row[prefix + 'What kind of place is it?'] == '' and row[prefix + 'Which country?'] == '' and row[prefix + 'VDC/Village'] == '' and row[prefix + 'District/State'] == '':
                continue
            
            index += 1
            lb = LocationBoxIndia()
            ordered_attrs = sorted(lb.__dict__.keys())
            for attr in ordered_attrs:
                if attr not in Command.lb_processing:
                    print('Unable to find processing rule for LB field ', attr)
                    self.missing_data = True
                    continue
                
                processing = Command.lb_processing[attr]
                processing['operation'](lb, attr, row, processing, prefix=prefix)
            
            lb.cif = cif
            lb.lb_number = index
            lb.save()
    
    def process_transportation(self, row, cif):
        kind = row["4.2 Primary means of travel?"]
        if kind != '':
            transport = TransporationIndia()
            transport.cif = cif
            transport.transportation_order_number = 1
            if kind in ['Bus', 'Local Bus', 'Micro Bus', 'Night bus', 'Sumo bus','Tourist Bus']:
                transport.transportation_kind = 'Bus'
                if kind != 'Bus':
                    transport.transportation_crossing = kind
            elif kind in ['by train ','Train']:
                transport.transportation_kind = 'Train'
            elif kind in ['Motobike', 'Red car', 'Van']:
                transport.transportation_kind = 'Vehicle'
                transport.transportation_crossing = kind
            elif kind == "Plane":
                transport.transportation_kind = 'Airport'
            
            transport.save()
            
                
                

            
    
    def process_vdf(self, row):
        vdf_number = row['VIF Number']
        vdfs = VdfIndia.objects.filter(vdf_number=vdf_number)
        if len(vdfs) > 0:
            self.existing_vdfs += 1
            return
        
        vdf = VdfIndia()
        ordered_attrs = sorted(vdf.__dict__.keys())
        for attr in ordered_attrs:
            if attr not in Command.vdf_processing:
                print('Unable to find processing rule for VDF field ', attr)
                self.missing_data = True
                continue
            
            processing = Command.vdf_processing[attr]
            processing['operation'](vdf, attr, row, processing)
        
        vdf.save()
        
        
