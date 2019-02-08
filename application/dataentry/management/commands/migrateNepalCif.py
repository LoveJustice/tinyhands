import numbers

from django.db import connection
from django.core.management.base import BaseCommand
from django.core.management.color import no_style

from dataentry.models import BorderStation, CifNepal, LocationBoxNepal, PersonBoxNepal, VictimInterview, VictimInterviewLocationBox, VictimInterviewPersonBox

class Command(BaseCommand):
    @staticmethod
    def process_constant(source, dest, name, config):
        value = config.get('value')
        setattr(dest, name, value)
    
    @staticmethod
    def process_or (source, dest, name, config):
        value = False
        for field in config.get('from_list'):
            tmp = getattr(source, field)
            if tmp:
                value = True
                break
        
        setattr(dest, name, value)
            
    
    @staticmethod
    def process_radio(source, dest, name, config):
        value = None
        for key, val in config['map_values'].items():
            tmp = getattr(source, key)
            if tmp == True:
                value = val
                break
        
        if value is None:
            key = config.get('other_value')
            if key is not None:
                value = getattr(source,key)
        
        setattr(dest, name, value)
        
    @staticmethod
    def change_name(source, dest, name, config):
        from_name = config.get('from_name')
        value = getattr(source, from_name)
        if value is not None:
            setattr(dest, name, value)
    
    @staticmethod
    def not_value(source, dest, name, config):
        from_name = config.get('from_name')
        value = getattr(source, from_name)
        if value is not None:
            setattr(dest, name, not value)
    
    @staticmethod
    def source_greater_zero(source, dest, name, config):
        from_name = config.get('from_name')
        value = getattr(source, from_name)
        if value is not None and isinstance(value, numbers.Number) and value > 0:
            setattr(dest, name, True)
        else:
            setattr(dest, name, False)
            
    @staticmethod
    def linked_other(source, dest, name, config):
        value = None
        for key, val in config['linked_values'].items():
            tmp = getattr(source, key)
            if tmp == True:
                value = val['prefix']
                if 'other_value' in val:
                    
                    other_value = val['other_value']
                    if other_value is not None and other_value != '':
                        value2 = getattr(source, other_value)
                        if value != '':
                            value = value + ' ' + value2
                        else:
                            value = value2

                break
        
        setattr(dest, name, value)
    
    @staticmethod    
    def legal_action_taken_filed_against(source, dest, name, config):
        tmp = getattr(source, 'legal_action_against_traffickers_fir_filed')
        if tmp:
            value = getattr(source, 'legal_action_fir_against_value')
            setattr(dest, 'legal_action_taken_filed_against', value)
        else:
            tmp = getattr(source, 'legal_action_against_traffickers_dofe_complaint')
            if tmp:
                value = getattr(source, 'legal_action_dofe_against_value')
                setattr(dest, 'legal_action_taken_filed_against', value)
    
    @staticmethod
    def append_value(dest_string, append_value):
        tmp = dest_string
        if append_value is not None and append_value != '':
            if dest_string is None or dest_string == '':
                tmp = append_value
            elif append_value is not None and append_value != '':
                tmp = dest_string + ',' + append_value
        
        return tmp
        
        
    @staticmethod
    def append_to(source, dest, name, config):
        append_elements = config.get('append_elements')
        dest_value = getattr(dest, name)
        for append_element in append_elements:
            from_name = append_element['from_name']
            value = getattr(source, from_name)
            if value is None:
                value = ''
            prefix = append_element.get('prefix', '')
            if 'check_value' in append_element:
                if value:
                    dest_value = Command.append_value(dest_value, prefix)
            elif value is not None and str(value) != '':
                dest_value = Command.append_value(dest_value, prefix + str(value))
        
        setattr(dest, name, dest_value)          
                
    @staticmethod
    def process_person_boxes(vif):
        pb_no_processing = [
                'case_filed_against',
                'arrested',
                'social_media',
                'relation_to_pv',
                'associated_lb',
                'pb_number'         # set in code
            ]
        pb_custom_processing = {
            'role':{
                    'operation':Command.process_radio,
                    'map_values':{
                        'who_is_this_role_broker':'Broker',
                        'who_is_this_role_companion':'Companion',
                        'who_is_this_role_india_trafficker':'India Trafficker',
                        'who_is_this_role_contact_of_husband':'Husband',
                        'who_is_this_role_known_trafficker':'Trafficker',
                        'who_is_this_role_manpower':'Manpower',
                        'who_is_this_role_passport':'ID Facilitator',
                        'who_is_this_role_sex_industry':'Sex Industry',
                    },
                },
            'appearance':{
                    'operation':Command.append_to,
                    'append_elements':[
                            {
                                'from_name':'height',
                                'prefix':'height='
                            },
                            {
                                'from_name':'weight',
                                'prefix':'weight='
                            },
                            {
                                'from_name':'physical_description_kirat',
                                'prefix':'Kirat',
                                'check_value': True
                            },
                            {
                                'from_name':'physical_description_sherpa',
                                'prefix':'Sherpa',
                                'check_value': True
                            },
                            {
                                'from_name':'physical_description_madeshi',
                                'prefix':'Madeshi',
                                'check_value': True
                            },
                            {
                                'from_name':'physical_description_pahadi',
                                'prefix':'Pahadi',
                                'check_value': True
                            },
                            {
                                'from_name':'physical_description_newari',
                                'prefix':'Newari',
                                'check_value': True
                            },
                            {
                                'from_name':'appearance_other',
                                'prefix':'',
                            },
                        ]
                },
                'occupation':{
                    'operation':Command.process_radio,
                    'map_values':{
                        'occupation_none':'None',
                        'occupation_agent':'Recruitment Agent',
                        'occupation_business_owner':'Business Owner',
                        'occupation_wage_labor':'Wage Labor',
                        'occupation_job_in_india':'Job in India',
                        'occupation_job_in_gulf':'Job in Gulf',
                        'occupation_farmer':'Farmer',
                        'occupation_teacher':'Teacher',
                        'occupation_police':'Police',
                        'occupation_army':'Army',
                        'occupation_guard':'Guard',
                        'occupation_cook':'Cook',
                        'occupation_driver':'Driver'
                    },
                    'other_value':'occupation_other_value'
                },
                'definitely_trafficked_many':{
                    'operation':Command.change_name,
                    'from_name':'interviewer_believes_definitely_trafficked'
                },
                'has_trafficked_some':{
                    'operation':Command.change_name,
                    'from_name':'interviewer_believes_have_trafficked'
                },
                'suspected_trafficker':{
                    'operation':Command.change_name,
                    'from_name':'interviewer_believes_suspects_trafficked'
                },
                'dont_believe_trafficker':{
                    'operation':Command.change_name,
                    'from_name':'interviewer_believes_not_trafficker'
                },
                'pv_definitely_trafficked_many':{
                    'operation':Command.change_name,
                    'from_name':'victim_believes_definitely_trafficked'
                },
                'pv_has_trafficked_some':{
                    'operation':Command.change_name,
                    'from_name':'victim_believes_have_trafficked'
                },
                'pv_suspected_trafficker':{
                    'operation':Command.change_name,
                    'from_name':'victim_believes_suspects_trafficked'
                },
                'pv_dont_believe_trafficker':{
                    'operation':Command.change_name,
                    'from_name':'victim_believes_not_trafficker'
                },
                'cif_id':{
                    'operation':Command.change_name,
                    'from_name':'victim_interview_id'
                },
                'flag_count': {
                    'operation':Command.process_constant,
                    'value':0
                },
            }
        
        source_pbs = VictimInterviewPersonBox.objects.filter(victim_interview = vif).order_by('id')
        pb_number = 1
        for source_pb in source_pbs:
            source_dict = source_pb.__dict__
            dest_pb = PersonBoxNepal()
            for attr in dest_pb.__dict__.keys():
                if attr in pb_custom_processing:
                    config = pb_custom_processing[attr]
                    operation = config['operation']
                    operation(source_pb, dest_pb, attr, config)
                elif attr not in pb_no_processing:
                    if attr not in source_dict:
                        print ('attribute', attr, 'not found in source PB')
                    
                    value = getattr(source_pb, attr)
                    setattr(dest_pb, attr, value)
            
            dest_pb.pb_number = pb_number
            dest_pb.save()
            
            pb_number = pb_number + 1
            
    @staticmethod
    def process_location_boxes(vif):
        lb_no_processing = [
                'country',
                'pv_stayed_not_applicable',
                'pv_stayed_days',
                'pv_stayed_start_date',
                'pv_attempt_hide_not_applicable',
                'pv_attempt_hide_no',
                'pv_attempt_hide_yes',
                'pv_attempt_hide_explaination',
                'pv_free_to_go_not_applicable',
                'pv_free_to_go_yes',
                'pv_free_to_go_no',
                'pv_free_to_go_explaination',
                'number_other_pvs_at_location',
                'lb_number'
            ]
        lb_custom_processing = {
            'place':{
                    'operation':Command.process_radio,
                    'map_values':{
                        'which_place_india_meetpoint':'Meet Point',
                        'which_place_manpower':'Recruitment Agency',
                        'which_place_transit_hideout':'Transit Location',
                        'which_place_destination':'Destination',
                        'which_place_passport':'Source of ID',
                        'which_place_nepal_meet_point':'Meet Point'
                    }
                },
            'place_kind':{
                'operation':Command.process_radio,
                'map_values':{
                    'what_kind_place_persons_house':'House',
                    'what_kind_place_bus_station':'Bus Station',
                    'what_kind_place_train_station':'Train Station',
                    'what_kind_place_shop':'Shopping',
                    'what_kind_place_factory':'Factory',
                    'what_kind_place_brothel':'Brothel',
                    'what_kind_place_hotel':'Hotel',
                }
            },
            'name_signboard':{
                'operation':Command.change_name,
                'from_name':'signboard'
            },
            'associated_pb':{
                'operation':Command.change_name,
                'from_name':'associated_with_person_value'
            },
            'cif_id':{
                'operation':Command.change_name,
                'from_name':'victim_interview_id'
            },
            'flag_count': {
                'operation':Command.process_constant,
                'value':0
            },
        }
        
        source_lbs = VictimInterviewLocationBox.objects.filter(victim_interview = vif).order_by('id')
        lb_number = 1
        for source_lb in source_lbs:
            source_dict = source_lb.__dict__
            dest_lb = LocationBoxNepal()
            for attr in dest_lb.__dict__.keys():
                if attr in lb_custom_processing:
                    config = lb_custom_processing[attr]
                    operation = config['operation']
                    operation(source_lb, dest_lb, attr, config)
                elif attr not in lb_no_processing:
                    if attr not in source_dict:
                        print ('attribute', attr, 'not found in source PB')
                    
                    value = getattr(source_lb, attr)
                    setattr(dest_lb, attr, value)
            
            dest_lb.lb_number = lb_number
            dest_lb.save()
            
            lb_number = lb_number + 1
        
        
        
    def handle(self, *args, **options):
        main_no_processing = [
                'informant_number',
                'social_media',
                'guardian_name',
                'recruited_agency_pb',
                'recruited_broker_pb',
                'how_recruited_promised_job',
                'how_recruited_married',
                'how_recruited_promised_marriage',
                'how_recruited_broker_online',
                'how_recruited_broker_online_pb',
                'how_recruited_broker_approached_pb',
                'how_recruited_broker_called_pv',
                'known_broker_pb',
                'married_broker_pb',
                'travel_expenses_broker_repaid_amount',
                'expected_earning_pb',
                'border_cross_night',
                'border_cross_off_road',
                'border_cross_foot',
                'id_source_pb',
                'permission_contact_pv',
                'permission_contact_whats_app',
                'permission_contact_facebook',
                'permission_contact_phone',
                'legal_action_taken_staff_do_not_believe',
                'legal_action_taken_staff_pv_does_not_believe',
                'legal_action_taken_staff_pv_threatened',
                'date_visit_police_station',
                'officer_name',
                'police_station_took_statement',
                'police_station_took_statement_privately',
                'police_station_victim_name_given_to_media',
                'police_station_gave_trafficker_access_to_pv',
                'police_interact_disrespectful',
                'police_interact_unprofessional',
                'police_interact_resistant_to_fir',
                'police_interact_none',
                'victim_statement_certified',
                'victim_statement_certified_date',
                'police_do_not_believe_crime',
                'police_say_not_enough_evidence',
                'trafficker_ran_away',
                'unable_to_locate_trafficker',
                'pv_will_not_testify',
                'delayed_waiting_for_other_traffickers',
                'police_are_scared',
                'suspect_corruption_or_bribes',
                'pv_think_would_have_been_trafficked',
                'exploitation_forced_prostitution_exp',
                'exploitation_forced_prostitution_occ',
                'exploitation_forced_prostitution_pb',
                'exploitation_forced_prostitution_lb',
                'exploitation_sexual_abuse_exp',
                'exploitation_sexual_abuse_pb',
                'exploitation_sexual_abuse_lb',
                'exploitation_physical_abuse_exp',
                'exploitation_physical_abuse_occ',
                'exploitation_physical_abuse_pb',
                'exploitation_physical_abuse_lb',
                'exploitation_debt_bondage_exp',
                'exploitation_debt_bondage_occ',
                'exploitation_debt_bondage_pb',
                'exploitation_debt_bondage_lb',
                'exploitation_forced_labor_exp',
                'exploitation_forced_labor_occ',
                'exploitation_forced_labor_pb',
                'exploitation_forced_labor_lb',
                'exploitation_organ_removal_exp',
                'exploitation_organ_removal_occ',
                'exploitation_organ_removal_pb',
                'exploitation_organ_removal_lb',
                'exploitation_other_exp',
                'exploitation_other_pb',
                'exploitation_other_lb',
                'reported_blue_flags',
                'total_blue_flags',
                'broker_relation',
                'expected_earning_currency',
                'purpose_for_leaving_job_massage',
                'case_exploration_under_16_separated',
                'case_exploration_under_18_sent_job',
                'case_exploration_under_16_sexually_abused',
                'case_exploration_female_18_30_gulf_country',
                'case_exploration_detained_against_will',
                'case_exploration_abused',
                'form_entered_by_id',
                'suspected_trafficker_count',
                'travel_expenses_paid_by_broker_pb',
                'travel_expenses_paid_by_broker_repaid_pb',
                'travel_expenses_paid_to_broker_pb'
            ]
        main_custom_processing = {
            'status': {
                    'operation':Command.process_constant,
                    'value':'approved'
                },
            'cif_number':{
                'operation':Command.change_name,
                    'from_name':'vif_number'
                },
            'staff_name':{
                'operation':Command.change_name,
                    'from_name':'interviewer'
                },
            'interview_date':{
                'operation':Command.change_name,
                    'from_name':'date'
                },
            'source_of_intelligence': {
                    'operation':Command.process_constant,
                    'value':'Intercept'
                },
            'incident_date':{
                'operation':Command.change_name,
                    'from_name':'date'
                },
            'pv_signed_form':{
                'operation':Command.change_name,
                    'from_name':'statement_read_before_beginning'
                },
            'consent_for_fundraising':{
                'operation':Command.change_name,
                    'from_name':'permission_to_use_photograph'
                },
            'occupation':{
                    'operation':Command.process_radio,
                    'map_values':{
                        'victim_occupation_unemployed':'unemployed',
                        'victim_occupation_farmer':'farmer',
                        'victim_occupation_wage_laborer':'wage laborer',
                        'victim_occupation_business_owner':'business owner',
                        'victim_occupation_migrant_worker':'migrant worker',
                        'victim_occupation_tailoring':'tailoring',
                        'victim_occupation_housewife':'housewife',
                        'victim_occupation_animal_husbandry':'animal husbandry',
                        'victim_occupation_domestic_work':'domestic work',
                        'victim_occupation_shopkeeper':'shopkeeper',
                        'victim_occupation_hotel':'hotel',
                        'victim_occupation_factory':'factory',
                    },
                    'other_value':'victim_occupation_other_value'
                },
            'education':{
                    'operation':Command.process_radio,
                    'map_values':{
                        'victim_education_level_none':'None/Illiterate',
                        'victim_education_level_informal':'Primary',
                        'victim_education_level_primary':'Primary',
                        'victim_education_level_grade_4_8':'Primary',
                        'victim_education_level_grade_9_10':'Secondary',
                        'victim_education_level_slc':'Secondary',
                        'victim_education_level_11_12':'Secondary',
                        'victim_education_level_bachelors':'University',
                        'victim_education_level_masters':'University'
                    }
                },
            'guardian_phone':{
                'operation':Command.change_name,
                    'from_name':'victim_guardian_phone'
                },
            'guardian_relationship':{
                    'operation':Command.process_radio,
                    'map_values':{
                        'victim_primary_guardian_own_parents':'Own Parent(s)',
                        'victim_primary_guardian_husband':'Other Relative',
                        'victim_primary_guardian_other_relative':'Other Relative',
                        'victim_primary_guardian_non_relative':'Non-relative',
                        'victim_primary_guardian_no_one':'No one(I have no guardian)'
                    }
                },
            'other_possible_victims':{
                'operation':Command.source_greater_zero,
                    'from_name':'how_many_others_in_situation'
                },
            'recruited_agency':{
                'operation':Command.change_name,
                    'from_name':'manpower_involved'
                },
            'recruited_no':{
                'operation':Command.not_value,
                    'from_name':'manpower_involved'
                },
            'recruited_broker':{
                'operation':Command.change_name,
                    'from_name':'victim_recruited_in_village'
                },
            'how_recruited_at_work':{
                'operation':Command.change_name,
                    'from_name':'victim_how_met_broker_at_work'
                },
            'how_recruited_at_school':{
                'operation':Command.change_name,
                    'from_name':'victim_how_met_broker_at_school'
                },
            'how_recruited_job_ad':{
                'operation':Command.change_name,
                    'from_name':'victim_how_met_broker_job_advertisement'
                },
            'how_recruited_broker_approached':{
                'operation':Command.change_name,
                    'from_name':'victim_how_met_broker_he_approached_me'
                },
            'how_recruited_broker_through_friends':{
                'operation':Command.change_name,
                    'from_name':'victim_how_met_broker_through_friends'
                },
            'how_recruited_broker_through_family':{
                'operation':Command.change_name,
                    'from_name':'victim_how_met_broker_through_family'
                },
            'how_recruited_broker_other':{
                    'operation':Command.linked_other,
                    'linked_values':{
                        'victim_how_met_broker_from_community':{'prefix':'from community'},
                        'victim_how_met_broker_at_wedding':{'prefix':'at wedding'},
                        'victim_how_met_broker_in_a_vehicle':{'prefix':'in vehicle'},
                        'victim_how_met_broker_in_a_hospital':{'prefix':'in hospital'},
                        'victim_how_met_broker_went_myself':{'prefix':'went myself'},
                        'victim_how_met_broker_called_my_mobile':{'prefix':'mobile:', 'other_value':'victim_how_met_broker_mobile_explanation'},
                        'victim_how_met_broker_other':{'prefix':'','other_value':'victim_how_met_broker_other_value'}
                        
                    },
                },
            'known_broker_years':{
                'operation':Command.change_name,
                    'from_name':'victim_how_long_known_broker_years'
                },
            'known_broker_months':{
                'operation':Command.change_name,
                    'from_name':'victim_how_long_known_broker_months'
                },
            'married_broker_years':{
                'operation':Command.change_name,
                    'from_name':'victim_married_to_broker_years'
                },
            'married_broker_months':{
                'operation':Command.change_name,
                    'from_name':'victim_married_to_broker_months'
                },
            'travel_expenses_paid_themselves':{
                'operation':Command.change_name,
                    'from_name':'victim_how_expense_was_paid_paid_myself'
                },
            'travel_expenses_paid_by_broker':{
                'operation':Command.change_name,
                    'from_name':'victim_how_expense_was_paid_broker_paid_all'
                },
            'travel_expenses_paid_to_broker':{
                'operation':Command.change_name,
                    'from_name':'victim_how_expense_was_paid_gave_money_to_broker'
                },
            'travel_expenses_paid_to_broker_amount':{
                'operation':Command.change_name,
                    'from_name':'victim_how_expense_was_paid_amount'
                },
            'travel_expenses_paid_by_broker_repaid':{
                'operation':Command.change_name,
                    'from_name':'victim_how_expense_was_paid_broker_gave_loan'
                },
            'expected_earning':{
                'operation':Command.change_name,
                    'from_name':'amount_victim_would_earn'
                },
            'purpose_for_leaving_education':{
                'operation':Command.change_name,
                    'from_name':'migration_plans_education'
                },
            'purpose_for_leaving_travel_tour':{
                'operation':Command.change_name,
                    'from_name':'migration_plans_travel_tour'
                },
            'purpose_for_leaving_marriage':{
                'operation':Command.process_or,
                    'from_list':['migration_plans_eloping','migration_plans_arranged_marriage']
                },
            'purpose_for_leaving_family':{
                'operation':Command.change_name,
                    'from_name':'migration_plans_meet_own_family'
                },
            'purpose_for_leaving_medical':{
                'operation':Command.change_name,
                    'from_name':'migration_plans_medical_treatment'
                },
            'purpose_for_leaving_job_hotel':{
                'operation':Command.change_name,
                    'from_name':'migration_plans_job_hotel'
                },
            'purpose_for_leaving_job_household':{
                'operation':Command.change_name,
                    'from_name':'migration_plans_job_household'
                },
            'purpose_for_leaving_other':{
                    'operation':Command.linked_other,
                    'linked_values':{
                        'migration_plans_shopping':{'prefix':'Shopping'},
                        'migration_plans_visit_brokers_home':{'prefix':"Visit broker's home"},
                        'migration_plans_job_broker_didnt_say':{'prefix':"Broker didn't say"},
                        'migration_plans_job_baby_care':{'prefix':'Baby care'},
                        'migration_plans_job_factory':{'prefix':'Factory'},
                        'migration_plans_job_shop':{'prefix':'Shop'},
                        'migration_plans_job_laborer':{'prefix':'Laborer'},
                        'migration_plans_job_brothel':{'prefix':'Brothel'},
                        'migration_plans_job_other':{'prefix':'Job', 'other_value':'migration_plans_job_other_value'},
                        'migration_plans_other':{'prefix':'', 'other_value':'migration_plans_other'}
                    },
                },
                             
            'planned_destination': {
                    'operation':Command.linked_other,
                    'linked_values':{
                        'victim_where_going_india_delhi':{'prefix':'Delhi, India'},
                        'victim_where_going_india_mumbai':{'prefix':'Mumbai, India'},
                        'victim_where_going_india_surat':{'prefix':'Surat, India'},
                        'victim_where_going_india_rajastan':{'prefix':'Rajastan, India'},
                        'victim_where_going_india_kolkata':{'prefix':'Kolkata, India'},
                        'victim_where_going_india_pune':{'prefix':'Pune, India'},
                        'victim_where_going_india_jaipur':{'prefix':'Jaipur, India'},
                        'victim_where_going_india_bihar':{'prefix':'Bihar, India'},
                        'victim_where_going_india_didnt_know':{'prefix':'Unknown location in India'},
                        'victim_where_going_india_other':{'prefix':'India', 'other_value':'victim_where_going_india_other_value'},
                        'victim_where_going_region_india':{'prefix':'India'},
                        'victim_where_going_gulf_lebanon':{'prefix':'Lebanon'},
                        'victim_where_going_gulf_dubai':{'prefix':'Dubai, UAE'},
                        'victim_where_going_gulf_malaysia':{'prefix':'Malaysia'},
                        'victim_where_going_gulf_oman':{'prefix':'Oman'},
                        'victim_where_going_gulf_saudi_arabia':{'prefix':'Saudi Arabia'},
                        'victim_where_going_gulf_kuwait':{'prefix':'Kuwait'},
                        'victim_where_going_gulf_qatar':{'prefix':'Qatar'},
                        'victim_where_going_gulf_didnt_know':{'prefix':'Unknown Gulf Location'},
                        'victim_where_going_gulf_other':{'prefix':'Gulf', 'other_value':'victim_where_going_gulf_other_value'},
                        'victim_where_going_region_gulf':{'prefix':'Unknown Gulf Location'}
                    }
                },
            'border_cross_vehicle':{
                    'operation':Command.process_or,
                    'from_list':['victim_primary_means_of_travel_tourist_bus', 'victim_primary_means_of_travel_motorbike',
                                 'victim_primary_means_of_travel_private_car', 'victim_primary_means_of_travel_local_bus',
                                 'victim_primary_means_of_travel_microbus']
                },
            'id_made_no':{
                'operation':Command.change_name,
                    'from_name':'passport_made_no_passport_made'
                },
            'id_made_real':{
                'operation':Command.change_name,
                    'from_name':'passport_made_real_passport_made'
                },
            'id_made_fake':{
                'operation':Command.change_name,
                    'from_name':'passport_made_passport_was_fake'
                },
            'id_made_false_name':{
                'operation':Command.change_name,
                    'from_name':'passport_made_passport_included_false_name'
                },
            'id_made_other_false':{
                'operation':Command.change_name,
                    'from_name':'passport_made_passport_included_false_name'
                },
            'id_kept_by_broker':{
                'operation':Command.change_name,
                    'from_name':'victim_passport_with_broker'
                },
            'legal_action_taken':{
                    'operation':Command.process_radio,
                    'map_values':{
                        'legal_action_against_traffickers_no':'no',
                        'legal_action_against_traffickers_fir_filed':'yes, case filed',
                        'legal_action_against_traffickers_dofe_complaint':'yes, case filed',
                    }
                },
            'legal_action_taken_case_type':{
                    'operation':Command.process_radio,
                    'map_values':{
                        'legal_action_against_traffickers_fir_filed':'FIR filed',
                        'legal_action_against_traffickers_dofe_complaint':'DoFE complaint',
                    }
                },
            'legal_action_taken_filed_against':{
                    'operation':Command.legal_action_taken_filed_against
                },
            'legal_action_taken_staff_police_not_enough_info':{
                'operation':Command.change_name,
                    'from_name':'reason_no_legal_police_not_enough_info'
                },
            'legal_action_taken_staff_trafficker_ran':{
                'operation':Command.change_name,
                    'from_name':'reason_no_legal_trafficker_ran_away'
                },
            'legal_action_taken_staff_trafficker_relative':{
                'operation':Command.change_name,
                    'from_name':'reason_no_legal_trafficker_is_own_people'
                },
            'legal_action_taken_staff_pv_afraid_reputation':{
                'operation':Command.change_name,
                    'from_name':'reason_no_legal_victim_afraid_of_reputation'
                },
            'legal_action_taken_staff_pv_afraid_safety':{
                'operation':Command.change_name,
                    'from_name':'reason_no_legal_victim_afraid_for_safety'
                },
            'legal_action_taken_staff_pv_or_family_bribed':{
                'operation':Command.change_name,
                    'from_name':'reason_no_legal_victim_family_bribed'
                },
            'legal_action_taken_staff_family_not_willing':{
                    'operation':Command.process_or,
                    'from_list':['reason_no_legal_family_afraid_of_reputation', 'reason_no_legal_family_afraid_for_safety']
                },
            'exploitation_sexual_abuse_occ':{
                'operation':Command.change_name,
                    'from_name':'abuse_happened_sexual_abuse'
                },
            'exploitation_other_occ':{
                'operation':Command.process_or,
                    'from_list':['abuse_happened_sexual_harassment','abuse_happened_physical_abuse',
                                 'abuse_happened_threats', 'abuse_happened_denied_proper_food',
                                 'abuse_happened_forced_to_take_drugs']
                },
            'exploitation_other_value':{
                'operation':Command.append_to,
                    'append_elements':[
                            {
                                'from_name':'abuse_happened_sexual_harassment',
                                'prefix':'sexual harassment',
                                'check_value': True
                            },
                            {
                                'from_name':'abuse_happened_physical_abuse',
                                'prefix':'physical abuse',
                                'check_value': True
                            },
                            {
                                'from_name':'abuse_happened_threats',
                                'prefix':'threats',
                                'check_value': True
                            },
                            {
                                'from_name':'abuse_happened_denied_proper_food',
                                'prefix':'denied proper food',
                                'check_value': True
                            },
                            {
                                'from_name':'abuse_happened_forced_to_take_drugs',
                                'prefix':'forced to take drugs',
                                'check_value': True
                            }
                    ]
                },
            'main_pv_id':{
                'operation':Command.change_name,
                    'from_name':'victim_id'
                },
            'station_id':{
                'operation':Command.change_name,
                    'from_name':'border_station_id'
                },
        }
        
        # Copy data from IRFs in Interception model to IrfNepal model
        print('Migrating VIFs')
        source_vifs = VictimInterview.objects.all()
        for source_vif in source_vifs:
            source_dict = source_vif.__dict__
            dest_cif = CifNepal()
            
            for attr in dest_cif.__dict__.keys():
                if attr in main_custom_processing:
                    config = main_custom_processing[attr]
                    operation = config['operation']
                    operation(source_vif, dest_cif, attr, config)
                elif attr not in main_no_processing:
                    if attr not in source_dict:
                        print ('attribute', attr, 'not found in source VIF')
                        
                    value = getattr(source_vif, attr)
                    setattr(dest_cif, attr, value)
            
            # Many VictimInterview entries do not have the border station field set, but it is required in the IrfNepal
            station_code = dest_cif.cif_number[:3].upper()
            station = BorderStation.objects.get(station_code=station_code)
            dest_cif.station = station          
            
            dest_cif.save()
            
            Command.process_person_boxes(source_vif)
            Command.process_location_boxes(source_vif)
        
        print ('Reset sequences')
        sequence_sql = connection.ops.sequence_reset_sql(no_style(), [CifNepal, PersonBoxNepal, LocationBoxNepal])
        with connection.cursor() as cursor:
            for sql in sequence_sql:
                cursor.execute(sql)
                
        print('Migration complete')
                    