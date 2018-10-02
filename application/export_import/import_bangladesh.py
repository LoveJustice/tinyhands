import csv
import pytz
from dateutil.parser import parse

from accounts.models import Account
from dataentry.form_data import FormData
from dataentry.validate_form import ValidateForm
from dataentry.models import Address1, Address2, BorderStation, Form, IrfBangladesh, IntercepteeBangladesh, Person, Question, QuestionStorage
from static_border_stations.models import Location

class ImportBangladesh:
    main_questions = {
        1:{    # IRF Number
                'columns':['IRF #']
           },
        2:{    # of Victims
                'columns':['# of Victims'],
                'default':0
           },
        3:{    # Location
                'columns':['Location']
           },
        4:{    # Date/Time of Interception
                'columns':['Date/Time of Intercept']
           },
        5:{    # of Traffickers
                'columns':['# of Traffickers'],
                'default':0
           },
        6:{    # Staff Name
                'columns':['Staff Name']
           },
        10:{    # Person appears drugged or drowsy
                'columns':['Red Flags'],
                'contains':'1.18 They appear drugged or drowsy'
            },
        12:{    # Alone
                'columns':['Red Flags'],
                'contains':'1.1 Traveling Alone'
            },
        13:{    # Husband/Wife
                'columns':['Red Flags'],
                'contains':'1.2 Traveling with Husband/Wife'
            },
        14:{    # Own brother, sister/relative
                'columns':['Red Flags'],
                'contains':'1.3 Own brother, sister, relative'
            },
        24:{    # Married in the past 2 weeks
                'columns':['Red Flags'],
                'contains':'1.12 Married in the past 2 weeks'
            },
        25:{    # Married within the past 2-8 weeks
                'columns':['Red Flags'],
                'contains':'1.13 Married in the past 2-8 weeks'
            },
        26:{    # Less than 2 weeks before eloping
                'columns':['Red Flags'],
                'contains':'1.14 Met less than 2 weeks before eloping'
            },
        27:{    # 2-12 weeks before eloping
                'columns':['Red Flags'],
                'contains':'1.15 Met 2-12 Weeks before eloping'
            },
        28:{    # Cast not the same as alleged relative
                'columns':['Red Flags'],
                'contains':'1.16 Family name not the same as alleged relative'
            },
        30:{    # Caught in a lie or contradiction
                'columns':['Red Flags'],
                'contains':'1.17 Caught in a lie or contradiction'
            },
        33:{    # Waiting for someone who fits description of trafficker
                'columns':['Red Flags'],
                'contains':'1.11 Waiting for someone who fits description of a trafficker'
            },
        34:{    # Known place in Bangladesh
                'columns':['RF 1.4 Known place in Bangladesh:'],
            },
        36:{    # Job
                'columns':['Red Flags'],
                'contains':'2.0 Going for a job'
            },
        39:{    # Study
                'columns':['Red Flags'],
                'contains':'2.1 Study'
            },
        46:{    # Heading for a border area
                'columns':['Red Flags'],
                'contains':'1.10 Heading for a border area'
            },
        51:{    # No address in India
                'columns':['Red Flags'],
                'contains':'2.3 No address in India'
            },
        52:{    # No company phone number
                'columns':['Red Flags'],
                'contains':'2.4 No company phone number'
            },
        53:{    # No appointment Letter
                'columns':['Red Flags'],
                'contains':'2.5 No appointment letter'
            },
        54:{    # Has a valid gulf country visa in passport
                'columns':['Red Flags'],
                'contains':'2.6 Has valid Middle East visa in passport'
            },
        55:{    # Passport is with a broker
                'columns':['Red Flags'],
                'contains':'2.7 Passport is with a broker'
            },
        56:{    # Job is too good to be true
                'columns':['Red Flags'],
                'contains':'2.18 Job details are too good to be true'
            },
        57:{    # Not a real job
                'columns':['Red Flags'],
                'contains':'2.8 Not a real job'
            },
        58:{    # Could not confirm job
                'columns':['Red Flags'],
                'contains':'2.9 Could not confirm job'
            },
        61:{    # No documentation of enrollment
                'columns':['Red Flags'],
                'contains':'2.12 No documentation of enrollment'
            },
        62:{    # Does not know school's name and location
                'columns':['Red Flags'],
                'contains':"2.13 Doesn't know school name / location"
            },
        63:{    # No phone number for school
                'columns':['Red Flags'],
                'contains':'2.14 No phone number for school'
            },
        64:{    # Not enrolled in school
                'columns':['Red Flags'],
                'contains':'2.17 Not enrolled in school'
            },
        69:{    # Running away from home (18 yrs or older)
                'columns':['Red Flags'],
                'contains':'2.19 Running away from home (18 years or older)'
            },
        70:{    # Running away from home (under 18 yrs old)
                'columns':['Red Flags'],
                'contains':'2.20 Running away from home (18 years or under)'
            },
        71:{    # Doesn't know details about village
                'columns':['Red Flags'],
                'contains':"3.0 Doesn't know details about village"
            },
        72:{    # Reluctant to give info about village
                # No data in spreadsheet
            },
        73:{    # Reluctant to give family info
                # No data in spreadsheet
            },
        74:{    # Will not give family info
                'columns':['Red Flags'],
                'contains':'3.3 Will not give family info.'
            },
        77:{    # No family contact established
                'columns':['Red Flags'],
                'contains':'3.4 No family contact made (under 18)'
            },
        78:{    #Family doesn't know where they are going
                'columns':['Red Flags'],
                'contains':"3.5 Family doesn't know they're going to India (under 18)"
            },
        79:{    # Family unwilling to let them go
                'columns':['Red Flags'],
                'contains':'3.6 Family unwilling to let them go (under 18)'
            },
        80:{    # Family members do not know where they are going
                'columns':['Red Flags'],
                'contains':"Family members don't know they are going to India (over 18)"
            },
        81:{    # Family members are unwilling to let them go
                'columns':['Red Flags'],
                'contains':"3.8 Family members unwilling to let them go (over 18)"
            },
        82:{    # Which family member did you talk to?
                'columns':['Which family member did you talk to?'],
                'map':{
                    '4.3 Own Father':'father',
                    '4.4 Own Mother':'mother',
                    '4.6 Own Aunt / Uncle':'aunt/uncle',
                    '4.1 Own Brother':'brother',
                    '4.5 Own Grandparents':'grandparent',
                    '4.2 Own Sister':'sister',
                    }
            },
        91:{    # How did you make the interception
                'columns':['How did you make the interception?'],
                'map':{
                     '7.0 Staff':'staff',
                     '6.0 Contact':'contact',
                     '6.0 Contact, 7.0 Staff':'contact'
                    }
            },
        92:{    # Contact who noticed
                'columns':['Type of Contact'],
                'map':{
                    '6.4 Bus driver':'Bus driver',
                    '6.7 Police':'Police',
                    '6.6 Other NGO':'Other NGO'
                    }
            },
        102:{    # Did you pay the contact for this information?
                # No data in spreadsheet
             },
        104:{    # How much?
                # No data in spreadsheet
             },
        106:{    # Staff who noticed
                'columns':['7.1 Staff who noticed:']
             },
        111:{    # Hesitant
                'columns':['What was the sign that made you stop them for questioning?'],
                'contains':'7.2 They were hesitant'
             },
        112:{    # Nervious or afraid
                'columns':['What was the sign that made you stop them for questioning?'],
                'contains':'7.3 They were nervous or affriad'
             },
        113:{    # Hurrying
                'columns':['What was the sign that made you stop them for questioning?'],
                'contains':'7.4 They were hurrying'
             },
        114:{    # Drugged or drowsy
                'columns':['What was the sign that made you stop them for questioning?'],
                'contains':'7.5 They appeared drugged or drowsy'
             },
        115:{    # New clothes
                'columns':['What was the sign that made you stop them for questioning?'],
                'contains':'7.6 They had new clothes'
             },
        116:{    # Dirty clothes
                'columns':['What was the sign that made you stop them for questioning?'],
                'contains':'7.7 They had dirty clothes'
             },
        117:{    # Carrying Full bags
                'columns':['What was the sign that made you stop them for questioning?'],
                'contains':'7.8 They were carrying full bags'
             },
        118:{    # Village Dress
                'columns':['What was the sign that made you stop them for questioning?'],
                'contains':'7.9 They had village dress'
             },
        119:{    # Indian looking
                'columns':['What was the sign that made you stop them for questioning?'],
                'contains':'7.10 They were Indian looking'
             },
        120:{    # Typical village look
                'columns':['What was the sign that made you stop them for questioning?'],
                'contains':'7.11 They had a typical village look'
             },
        121:{    # Looked like agent
                'columns':['What was the sign that made you stop them for questioning?'],
                'contains':'7.12 They looked like an agent'
             },
        122:{    # Caste difference
                'columns':['What was the sign that made you stop them for questioning?'],
                'contains':'7.13 There was a racial difference'
             },
        123:{    # Young looking
                'columns':['What was the sign that made you stop them for questioning?'],
                'contains':'7.14 They were young looking'
             },
        124:{    # Waiting/sitting
                'columns':['What was the sign that made you stop them for questioning?'],
                'contains':'7.15 They were waiting / sitting'
             },
        126:{    # Roaming around
                'columns':['What was the sign that made you stop them for questioning?'],
                'contains':'7.17 They were roaming around'
             },
        127:{    # Exiting vehicle
                'columns':['What was the sign that made you stop them for questioning?'],
                'contains':'7.18 They were exiting a vehicle'
             },
        128:{    # Heading to vehicle
                'columns':['What was the sign that made you stop them for questioning?'],
                'contains':'7.19 They were heading to a vehicle'
             },
        129:{    # In a vehicle
                'columns':['What was the sign that made you stop them for questioning?'],
                'contains':'7.20 They were in a vehicle'
             },
        130:{    # In a rickshaw
                'columns':['What was the sign that made you stop them for questioning?'],
                'contains':'7.21 They were in a rickshaw'
             },
        131:{    # In a cart
                'columns':['What was the sign that made you stop them for questioning?'],
                'contains':'7.22 They were in a cart'
             },
        132:{    # Carrying a baby
                'columns':['What was the sign that made you stop them for questioning?'],
                'contains':'7.23 They were carrying a baby'
             },
        133:{    # On the phone
                'columns':['What was the sign that made you stop them for questioning?'],
                'contains':'7.24 They were on the phone'
             },
        135:{    # Walking to border
                'columns':['What was the sign that made you stop them for questioning?'],
                'contains':'7.16 They were walking to the border'
             },
        141:{    # Type of Intercept
                'columns':['Type of Intercept'],
                'map':{
                     '9.1 Middle East Trafficking':'middle east',
                     '9.4 Runaway':'runaway',
                     '9.2 India Trafficking':'india',
                     '9.3 In-Country Trafficking':'internal bangladesh'
                    }
             },
        142:{    # What is the primary reason you believed this case qualified?
                'columns':['RF 3.9 Additional information about interception:'],
             },
        143:{    # Reported Total Red Flag Points
                'columns':['5.0 Total Red Flag Points'],
             },
        144:{    # Total Red Flags
                # No data
             },
        146:{    # Case Narrative
                'columns':['Case Narrative (Interception Story)'],
             },
        147:{    # How sure are you that it was trafficking case?
                'columns':['9.7 How sure are you that it was a trafficking case?'],
             },
        151:{    # Scanned form has signature
                'columns':['Is the form signed?'],
             },
        152:{    # Attach scanned copy of form (pdf or image)
                # No data
             },
        252:{    # Wife/girl is Nepali/Bengali and under 18
                'columns':['Red Flags'],
                'contains':'Wife is under 18'
             },
        256:{    # Call Project Manager to confirm interept
                'columns':['Procedures'],
                'contains':'Called Cell Leader / Transit Monitoring Manager'
             },
        265:{    # Scan and submint OG the same day
                # duplicate of 286
                #'columns':['Procedures'],
                #'contains':'Scanned and submitted to OG the same day'
             },
        266:{    # Border Area
                'columns':['Red Flags'],
                'contains':'1.5 Going to border area'
             },
        267:{    # India
                'columns':['Red Flags'],
                'contains':'Going to India'
             },
        268:{    # Middle East
                'columns':['Red Flags'],
                'contains':'Going to the Middle East'
            },
        269:{    # Don't know
                'columns':['Red Flags'],
                'contains':"Don't know where they are going"
             },
        270:{    # Other Destination
                'columns':['RF 1.9 Other Destination:'],
             },
        271:{    # Other Purpose
             },
        286:{    # Scan and submit to OG same day
                'columns':['Procedures'],
                'contains':'Scanned and submitted to OG the same day'
             }
        }
    
    victim_questions={
        7:{    # Image
           },
        8:{    # Type
                'constant':'v'
           },
        9:{    # Person
           },
        15:{    # Relation to
            },
        }
    trafficker_question={
        7:{    # Image
           },
        8:{    # Type
            
           },
        9:{    # Person
           },
        15:{    # Relation to
            },
        11:{    # Taken into police custody
            },
        }
    
    def process(self, in_file):
        self.create_address1s()

        self.form = Form.objects.get(form_name='irfBangladesh')
        renumber = {}
        count = 1
        with open('import_bangladesh/renumber.csv') as renum:
            reader = csv.DictReader(renum)
            for row in reader:
                renumber[count] = {'old':row['Old'],'new':row['New']}
                count += 1
        
        self.cleaned = {}
        with open('import_bangladesh/cleaned_address.csv') as cleaned_address:
            reader = csv.DictReader(cleaned_address)
            for row in reader:
                irf_number = row['IRF #']
                if irf_number is not None and irf_number.strip() != '':
                    self.cleaned[irf_number] = row              
                
        count = 1
        with open(in_file) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.process_row(row, renumber[count])
                count += 1
    
    def process_row(self, in_row, renum):
        irf = IrfBangladesh()
        row = dict(in_row)
        
        irf_number = row['IRF #'].strip()
        if irf_number in self.cleaned:
            cleaned_addresses = self.cleaned[irf_number]
        else:
            print('Unable to find new address for IRF # ', irf_number)
            return
        
        if irf_number == renum['old'].strip():
            row['IRF #'] = renum['new']
        else:
            print('renumber fail ',row['IRF #'],renum['old'])
            return
            
        
        station_code = renum['new'][:3]
        if station_code is None:
            print ('Unable to process row with Station Code of None')
            return
        try:
            station = BorderStation.objects.get(station_code=station_code)
        except Exception:
            print('Unable to locate station for code ' + station_code)
            return
        
        location_name = row['Location']
        if location_name is not None and location_name.strip() != '':
            existing = Location.objects.filter(name=location_name, border_station = station)
            if len(existing) < 1:
                location = Location()
                location.name = location_name
                location.border_station = station
                location.save()
        
        irf.entered_by = Account.objects.get(id=10022)
        
        irf.station = station
        irf.status = 'in-progress'
        for question_id in ImportBangladesh.main_questions.keys():
            entry = ImportBangladesh.main_questions[question_id]
            if 'columns' not in entry:
                continue
            
            if len(entry['columns']) > 1:
                pass
            else:
                column = entry['columns'][0]
                value = row[column]
                question = Question.objects.get(id=question_id)
                #print('<<<<',question.export_name, '>>>>', value)
                if 'contains' in entry:
                    if value is not None and entry['contains'] in value:
                        result = True
                    else:
                        result = False
                elif 'map' in entry:
                    if value in entry['map']:
                        result = entry['map'][value]
                    else:
                        result = value
                elif question.answer_type.name == 'Checkbox' and (question.params is None or 'textbox' not in question.params):
                    if value is None or value.upper() == 'NO':
                        result = False
                    elif value.upper() == 'YES':
                        result = True
                elif question.answer_type.name == 'DateTime':
                    local_time = parse(value)
                    tz = pytz.timezone(station.time_zone)
                    result = tz.localize(local_time) 
                elif ((question.answer_type.name == 'Integer' or question.answer_type.name == 'Float') and 
                      (value is None or value.strip() == '')):
                    result = 0
                else:
                    result = value
            
            if (result is None or result == '') and 'default' in entry:
                result = entry['default'] 
            
            storage = QuestionStorage.objects.get(question_id = question_id)
            setattr(irf, storage.field_name, result)
            
        if irf.irf_number is None or irf.irf_number == '':
            return
        try:
            irf.save()
        except Exception as exc:
            print (irf.irf_number, exc.args[0])
            return
        
        for idx in range(1,3):
            prefix = 'Victim ' + str(idx) + ' '
            addr_prefix = 'V' + str(idx) + ' '
            self.create_interceptee(row, 'v', prefix, addr_prefix, irf, cleaned_addresses)
            
        
        for idx in range(1,3):
            prefix = 'Trafficker ' + str(idx) + ' '
            addr_prefix = 'T' + str(idx) + ' '
            self.create_interceptee(row, 't', prefix, addr_prefix, irf, cleaned_addresses)
        
        irf.status = 'approved'
        form_data = FormData(irf, self.form)
        validate = ValidateForm(self.form, form_data, True)
        validate.validate()
        if len(validate.errors) < 1:
            irf.save()
    
    def create_address1s(self):
        with open('import_bangladesh/geo.csv') as geo:
            reader = csv.DictReader(geo)
            for row in reader:
                name = row['Address 1'].strip()
                if name is None or name == '':
                    continue
                addresses = Address1.objects.filter(name=name)
                if len(addresses) > 0:
                    continue
                
                address1 = Address1()
                address1.name = name
                tmp = row['A1Lat']
                if tmp is None or tmp == '':
                    tmp = 0.0
                address1.latitude = tmp
                tmp = row['A1Long']
                if tmp is None or tmp == '':
                    tmp = 0.0
                address1.longitude = tmp
                address1.level = 'District'
                address1.save()
    
    def check_create_address1(self, row, cleaned_address, prefix):
        addr_name = cleaned_address[prefix + 'Address 1']
        if addr_name is None or addr_name.strip() == '':
            return None
        
        addresses = Address1.objects.filter(name=addr_name)
        if len(addresses) < 1:
            print('Address 1 not found for name', addr_name)
            return None
        else:
            address1 = addresses[0]
        
        return address1
        
    def check_create_address2(self, row, cleaned_address, prefix, address1):
        addr_name = cleaned_address[prefix + 'Address 2']
        if addr_name is None or addr_name.strip() == '':
            addr_name = 'Unknown'
        
        addresses = Address2.objects.filter(name=addr_name, address1 = address1)
        if len(addresses) < 1:
            address2 = Address2()
            address2.name = addr_name
            address2.level = row[prefix + 'Address 2 Level']
            address2.address1 = address1
            address2.save()
        else:
            address2 = addresses[0]
        
        return address2        
        
                
    def create_interceptee(self, row, kind, prefix, address_prefix, irf, cleaned_addresses):   
        name = row[prefix + 'Full Name']
        if name is None or name.strip() == '':
            # Cannot create if we do not have a name
            return None
        else:
            name = name.strip()
        
        person = Person()
        person.full_name = name
        gender = row[prefix + 'Gender']
        if gender is None or gender == '':
            gender = 'U'
        elif gender.upper() == 'MALE' or gender.upper() == 'M':
            gender = 'M'
        elif gender.upper() == 'FEMALE' or gender.upper() == 'F':
            gender = 'F'
        else:
            gender = 'U'
        person.gender = gender
        age = row[prefix + 'Age']
        if age is not None and age.strip() == '':
            age = None
        person.age = age
        person.phone_contact = row[prefix + 'Phone Contact']
        person.address1 = self.check_create_address1(row, cleaned_addresses, address_prefix)
        if person.address1 != None:
            person.address2 = self.check_create_address2(row, cleaned_addresses, address_prefix, person.address1)
        person.save()
        
        interceptee = IntercepteeBangladesh()
        interceptee.kind = kind
        interceptee.relation_to = row[prefix + "Relation to..."]
        interceptee.person = person
        if kind == 't' and row['9.6 Was any trafficker taken into police custody? If so list name:'] is not None and name in row['9.6 Was any trafficker taken into police custody? If so list name:']:
            interceptee.trafficker_taken_into_custody = True
        else:
            interceptee.trafficker_taken_into_custody = False
        interceptee.interception_record = irf
        interceptee.save()
        
        return interceptee
