from django.db import connection
from django.core.management.base import BaseCommand
from django.core.management.color import no_style

from dataentry.models import BorderStation, InterceptionRecord, IrfNepal, Interceptee, IntercepteeNepal

class Command(BaseCommand):
    @staticmethod
    def process_constant(source, dest, name, config, interceptees):
        value = config.get('value')
        setattr(dest, name, value)
    
    @staticmethod
    def process_no_value(source, dest, name, config, interceptees):
        pass
    
    @staticmethod
    def process_or (source, dest, name, config, interceptees):
        value = False
        for field in config.get('from_list'):
            tmp = getattr(source, field)
            if tmp:
                value = True
                break
        
        setattr(dest, name, value)
            
    
    @staticmethod
    def process_radio(source, dest, name, config, interceptees):
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
    def process_red_flags(source, dest, name, config, interceptees):
        value = source.calculate_total_red_flags()
        setattr(dest, name, value)
        
    @staticmethod
    def change_name(source, dest, name, config, interceptees):
        from_name = config.get('from_name')
        value = getattr(source, from_name)
        setattr(dest, name, value)
    
    @staticmethod
    def victim_between_18_and_23(source, dest, name, config, victims):
        from_name = config.get('from_name')
        value = getattr(source, from_name)
        set_value = False
        if value:
            set_value = False
            for interceptee in victims:
                if (interceptee.person is not None and interceptee.person.age is not None and
                    interceptee.person.age >=18 and interceptee.person.age <= 23):
                    set_value = True
                    break
        
        setattr(dest,name, set_value)
    
    @staticmethod
    def victim_over_23(source, dest, name, config, victims):
        from_name = config.get('from_name')
        value = getattr(source, from_name)
        set_value = False
        if value:
            for interceptee in victims:
                if (interceptee.person is not None and interceptee.person.age is not None and
                    interceptee.person.age >=18 and interceptee.person.age <= 23):
                    # If there is a victim of age between 18 and 23, then this flag should not be set
                    set_value = False
                    break
                if (interceptee.person is not None and (interceptee.person.age is None or
                    interceptee.person.age > 23)):
                    set_value = True
        
        setattr(dest,name, set_value)
        
    def handle(self, *args, **options):
        custom_processing = {
            'status': {
                    'operation':Command.process_constant,
                    'value':'approved'
                },
            'where_going_destination': {
                    'operation':Command.process_no_value,
                },
            'where_runaway': {
                    'operation':Command.process_or,
                    'from_list':['running_away_over_18', 'running_away_under_18']
                },
            'talked_to_family_member':{
                    'operation':Command.process_radio,
                    'map_values':{
                        'talked_to_family_member_brother':'brother',
                        'talked_to_family_member_sister':'sister',
                        'talked_to_family_member_father':'father',
                        'talked_to_family_member_mother':'mother',
                        'talked_to_family_member_grandparent':'grandparent',
                        'talked_to_family_member_aunt_uncle':'aunt/uncle',
                    },
                    'other_value':'talked_to_family_member_other_value'
                },
            'computed_total_red_flags':{
                    'operation':Command.process_red_flags
                },
            'who_noticed':{
                    'operation':Command.process_radio,
                    'map_values':{
                        'staff_noticed':'staff',
                        'contact_noticed':'contact'

                    }
                },
            'type_of_intercept':{
                    'operation':Command.process_radio,
                    'map_values':{
                        'interception_type_gulf_countries':'gulf',
                        'interception_type_india_trafficking':'india',
                        'interception_type_unsafe_migration':'unsafe_migration',
                        'interception_type_circus':'circus',
                        'interception_type_runaway':'runaway'
                    }
                },
            'convinced_by_staff':{
                    'operation':Command.process_no_value,
                },
            'convinced_by_family':{
                    'operation':Command.process_no_value,
                },
            'convinced_by_police':{
                    'operation':Command.process_no_value,
                },
            'which_contact':{
                    'operation':Command.process_radio,
                    'map_values':{
                        'which_contact_hotel_owner':'Hotel owner',
                        'which_contact_rickshaw_driver':'Rickshaw driver',
                        'which_contact_taxi_driver':'Taxi driver',
                        'which_contact_bus_driver':'Bus driver',
                        'which_contact_church_member':'Church member',
                        'which_contact_other_ngo':'Other NGO',
                        'which_contact_police':'Police',
                        'which_contact_subcommittee_member':'Subcomittee member',
                    },
                    'other_value':'which_contact_other_value'
                },
            'going_to_gulf_through_india': {
                    'operation':Command.process_no_value,
                },
            'traveling_with_someone_not_with_them':{
                    'operation':Command.change_name,
                    'from_name':'traveling_with_someone_not_with_her'
                },
            'no_address_at_destination':{
                    'operation':Command.change_name,
                    'from_name':'no_address_in_india'
                },
            'noticed_foreign_looking':{
                    'operation':Command.change_name,
                    'from_name':'noticed_indian_looking'
                },
            'station_id':{
                    'operation':Command.change_name,
                    'from_name':'border_station_id'
                },
            'group_missed_call': {
                    'operation':Command.process_no_value,
                },
            'group_facebook': {
                    'operation':Command.process_no_value,
                },
            'group_other_website': {
                    'operation':Command.process_no_value,
                },
            'who_in_group_engaged': {
                    'operation':Command.process_no_value,
                },
            'who_in_group_dating': {
                    'operation':Command.process_no_value,
                },
            'relationship_to_get_married': {
                    'operation':Command.process_no_value,
                },
            'contradiction_between_stories': {
                    'operation':Command.process_no_value,
                },
            'where_going_someone_paid_expenses': {
                    'operation':Command.process_no_value,
                },
            'family_doesnt_know_where_going_18_23': {
                    'operation':Command.victim_between_18_and_23,
                    'from_name':'over_18_family_doesnt_know'
                },
            'family_unwilling_to_let_go_18_23': {
                    'operation':Command.victim_between_18_and_23,
                    'from_name':'over_18_family_unwilling'
                },
            'over_23_family_unwilling_to_let_go': {
                    'operation':Command.victim_over_23,
                    'from_name':'over_18_family_unwilling'
                },
            'noticed_on_train': {
                    'operation':Command.process_no_value,
                },
            'reason_for_intercept': {
                    'operation':Command.process_no_value,
                },
            'evidence_categorization': {
                    'operation':Command.process_no_value,
                },
        }
        
        # Copy data from IRFs in Interception model to IrfNepal model
        print('Migrating IRFs')
        source_irfs = InterceptionRecord.objects.all()
        for source_irf in source_irfs:
            interceptees = Interceptee.objects.filter(interception_record = source_irf, kind = 'v')
            source_dict = source_irf.__dict__
            dest_irf = IrfNepal()
            
            for attr in dest_irf.__dict__.keys():
                if attr in custom_processing:
                    config = custom_processing[attr]
                    operation = config['operation']
                    operation(source_irf, dest_irf, attr, config, interceptees)
                else:
                    if attr not in source_dict:
                        print ('attribute', attr, 'not found in source IRF')
                        
                    value = getattr(source_irf, attr)
                    setattr(dest_irf, attr, value)
            
            # Many InterceptionRecord entries do not have the border station field set, but it is required in the IrfNepal
            station_code = dest_irf.irf_number[:3]
            station = BorderStation.objects.get(station_code=station_code)
            dest_irf.station = station          
            
            dest_irf.save()
            
            # Add location if it is not already present for the station
            #tmp = Location.objects.filter(border_station=station, name=source_irf.location)
            #if len(tmp) < 1:
                #location = Location()
                #location.name = source_irf.location
                #location.border_station = station
                #location.save()
        
        # Copy data from interceptees in Interceptee model to IntercepteeNepal model
        print('Migrating Interceptees')
        source_interceptees = Interceptee.objects.all()
        for source_interceptee in source_interceptees:
            dest_interceptee = IntercepteeNepal()
            dest_interceptee.id = source_interceptee.id
            dest_interceptee.photo = source_interceptee.photo
            dest_interceptee.kind = source_interceptee.kind
            dest_interceptee.relation_to = source_interceptee.relation_to
            setattr(dest_interceptee, 'interception_record_id', source_interceptee.interception_record.id)
            dest_interceptee.person = source_interceptee.person
            dest_interceptee.trafficker_taken_into_custody = False
            dest_interceptee.save()  
        
        # Set taken into custody in IntercepteeNepal model
        print ('Setting taken into custody flag')
        source_irfs = InterceptionRecord.objects.exclude(trafficker_taken_into_custody__isnull=True).exclude(trafficker_taken_into_custody__exact='')
        for source_irf in source_irfs:
            source_interceptees = Interceptee.objects.filter(interception_record=source_irf).order_by('id')
            taken_list = source_irf.trafficker_taken_into_custody.replace(':',',').replace(' ',',').split(',')
            for taken in taken_list:
                if taken == '':
                    continue;
                if not taken.isdigit():
                    print ('Non-integer taken into custody index.  irf_number=', source_irf.irf_number, 'index=', taken)
                    continue
                idx = int(taken)
                if idx < 1 or idx > len(source_interceptees):
                    print ('Taken into custody index out of range.  irf_number=', source_irf.irf_number, 'index=', taken)
                    continue
                if source_interceptees[idx-1].kind != 't':
                    print('Warning, taken into custody flag being appied to a victim interceptee.  irf_number=', source_irf.irf_number)
                dest_interceptee = IntercepteeNepal.objects.get(id=source_interceptees[idx - 1].id)
                dest_interceptee.trafficker_taken_into_custody = True
                dest_interceptee.save()
        
        print ('Reset sequences')
        sequence_sql = connection.ops.sequence_reset_sql(no_style(), [IrfNepal,IntercepteeNepal])
        with connection.cursor() as cursor:
            for sql in sequence_sql:
                cursor.execute(sql)
                
        print('Migration complete')
                    