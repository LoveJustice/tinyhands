import csv
import json
import re
import requests
import traceback
from datetime import date
from django.db import transaction, IntegrityError
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from dataentry.models import Country, Form, IrfCommon, LocationForm, Suspect, SuspectLegalPv, VdfCommon, Question, \
    QuestionStorage, QuestionLayout, FormCategory, IntercepteeCommon

# Rules for vulnerable questions (section 1) in IRF
# question_tag - the tag to be unset/set by the rule
# conflict_tag - a list of tags that if set, then this tag may not be set
# logic - python code to be evaluated to a True/False value indicating the value for the tag
# Note: assumes variable age has been set to none or the PVs age
BASE_VULNERABLE_RULES = [
    {
        'question_tag': 'irfAge0to5.2024.8',
        'conflict_tags': [],
        'logic': 'age is not None and age <= 5'
    },
    {
        'question_tag': 'irfAge6to9.2024.8',
        'conflict_tags': [],
        'logic': 'age is not None and age >= 6 and age <= 9'
    },
    {
        'question_tag': 'irfAge10to14.2024.8',
        'conflict_tags': [],
        'logic': 'age is not None and age >= 10 and age <= 14'
    },
    {
        'question_tag': 'irfAge15to17.2024.8',
        'conflict_tags': [],
        'logic': 'age is not None and age >= 15 and age <= 17'
    },
    {
        'question_tag': 'irfAge18to22.2024.8',
        'conflict_tags': [],
        'logic': 'age is not None and age >= 18 and age <= 22'
    },
    {
        'question_tag': 'irfAge23to29.2024.8',
        'conflict_tags': [],
        'logic': 'age is not None and age >= 23 and age <= 29'
    },
    {
        'question_tag': 'irfAge30to35.2024.8',
        'conflict_tags': [],
        'logic': 'age is not None and age >= 30 and age <= 35'
    },
    {
        'question_tag': 'irfFemale.2024.8',
        'conflict_tags': [],
        'logic': 'interceptee.person.gender=="F"'
    },
    {
        'question_tag': 'irfMinorNoGuardian.2024.8',
        'conflict_tags': ['irfAge18to22.2024.8', 'irfAge23to29.2024.8', 'irfAge30to35.2024.8'],
        'logic': 'irf.vulnerability_minor_without_guardian == True'
    },
    {
        'question_tag': 'irfSeductive.2024.8',
        'conflict_tags': [],
        'logic': '"wearing revealing clothing" in irf.profile.lower()'
    },
    {
        'question_tag': 'irfUnemployed.2024.8',
        'conflict_tags': ['irfAge0to5.2024.8', 'irfAge6to9.2024.8', 'irfAge10to14.2024.8',
                          'irfAge15to17.2024.8', 'irfMinorNoGuardian.2024.8'],
        'logic': '"unemployed" in irf.profile.lower()'
    },
    {
        'question_tag': 'irfInsufficientResources.2024.8',
        'conflict_tags': [],
        'logic': 'irf.vulnerability_insufficient_resource == True'
    },
    {
        'question_tag': 'irfNoPhone.2024.8',
        'conflict_tags': [],
        'logic': 'irf.vulnerability_no_mobile_phone == True'
    },
    {
        'question_tag': 'irfRecentlyEnslaved.2024.8',
        'conflict_tags': [],
        'logic': '"recently enslaved" in irf.profile.lower()'
    },
    {
        'question_tag': 'irfFirstTimeTravelingAbroad.2024.8',
        'conflict_tags': [],
        'logic': 'irf.vulnerability_first_time_traveling_abroad == True'
    },
    {
        'question_tag': 'irfRunaway.2024.8',
        'conflict_tags': [],
        'logic': '"runaway" in irf.profile.lower()'
    },
    {
        'question_tag': 'irfFirstTimeTravelingToCity.2024.8',
        'conflict_tags': [],
        'logic': 'irf.vulnerability_first_time_traveling_to_city == True'
    },
    {
        'question_tag': 'irfTravelingWithSomeoneRecentlyMet.2024.8',
        'conflict_tags': [],
        'logic': 'irf.vulnerability_travel_met_recently == True'
    },
    {
        'question_tag': 'irfStrandedAbandoned.2024.8',
        'conflict_tags': [],
        'logic': 'irf.vulnerability_stranded_or_abandoned == True'
    },
]

# Rules for industry questions
# question_tag - the tag to be unset/set by the rule
# logic - python code to be evaluated to a True/False value indicating the value for the tag
# Note: assumes industry field has by split and individual value is in the variable industry_part
BASE_INDUSTRY_RULES = [
    {
        'question_tag': 'irfDomesticWork.2024.8',
        'logic': "'domestic work' in industry_part.lower()"
    },
    {
        'question_tag': 'irfMassage.2024.8',
        'logic': "'spa/massage' in industry_part.lower()"
    },
    {
        'question_tag': 'irfMassage.2024.8',
        'logic': "'spa/massage' in industry_part.lower()"
    },
    {
        'question_tag': 'irfMassage.2024.8',
        'logic': "'massage parlor' in industry_part.lower()"
    },
    {
        'question_tag': 'irfDanceBar.2024.8',
        'logic': "'dance' in industry_part.lower()"
    },
]

# Map industry values to more common name
CONVERT_INDUSTRY = [
    {
        'pattern': 'Farm',
        'value': 'Agriculture',
    },
    {
        'pattern': 'Cleaner',
        'value': 'Cleaning',
    },
    {
        'pattern': 'Hotel',
        'value': 'Hospitality',
    },
    {
        'pattern': 'Supermarket',
        'value': 'Retail',
    },
    {
        'pattern': 'Waitress',
        'value': 'Waitress',
    },
    {
        'pattern': '^Factory$',
        'value': 'Manufacturing',
    },
    {
        'pattern': 'Herding',
        'value': 'Agriculture',
    },
    {
        'pattern': 'Security Guard',
        'value': 'Security',
    },
    {
        'pattern': 'Cashier',
        'value': 'Retail',
    },
    {
        'pattern': 'Restaurant',
        'value': 'Hospitality',
    },
    {
        'pattern': 'Garment',
        'value': 'Garment work',
    },
    {
        'pattern': 'Hawking',
        'value': 'Hawking',
    },
    {
        'pattern': 'Gardener',
        'value': 'Agriculture',
    },
    {
        'pattern': 'Mining',
        'value': 'Mine',
    },
    {
        'pattern': 'Nanny',
        'value': 'Domestic work',
    },
    {
        'pattern': 'Sales consultant',
        'value': 'Marketing',
    },
    {
        'pattern': 'Construction Work',
        'value': 'Construction',
    },
    {
        'pattern': 'Salonist',
        'value': 'Salon',
    },
]

# List of acceptable industry other values for migration
INDUSTRY_OTHER = [
    'Agriculture',
    'Street vendor',
    'Child Labour',
    'Cleaning',
    'Mine',
    'Hotel',
    'Construction',
    'Bonded Labour',
    'Fishing',
    'Security',
    'Packer',
    'Begging',
    'Hawking',
    'Driver',
    'Hospitality',
    'Retail',
    'Manufacturing',
    'Garment work',
    'Salon',
    'Brick Kiln',
    'Waitress',
    'Marketing',
]

# list of countries/cities known for trafficking
KNOWN_FOR_TRAFFICKING = [
    # Argentina
    'Village 31', 'Tierra del Fuego', 'Comodoro Rivadavia', 'Río Negro', 'Once', 'Usuahia', 'Santa Cruz', 'Neuquen',
    'Bajo Flores', 'Chubut', 'Mar del Plata', 'Mendoza',
    # Bangladesh
    'Delhi', 'Gulf Country', 'Mumbai',
    # Benin
    'Abuja', 'Porto Novo', 'Yamoussoukro', 'Kuwait', 'Librevielle',
    # Burkina Faso
    'Ouagadougou', 'Abidjan', 'Yamoussoukro', 'Rome', 'Tripoli', 'Riyadh',
    # Burundi
    'Bujumbura', 'Cibtoke', 'Kigali', 'Nairobi', 'Mombasa', 'UAE', 'Kampala', 'Oman', 'Qatar',
    # Cambodia
    'Thailand', 'China', 'Malaysia', 'Vietnam', 'Siem Reap', 'Phnom Penh', 'Sihanoukville',
    # Ecuador
    'Quito', 'Bogota', 'Lima', 'Buenos Aires', 'Santo Domingo', 'Quevedo', 'Latacunga', 'Sucumbois', 'Sucumbios',
    'Tulcan', 'Huaquillas', 'Esmeraldas',
    # Ethiopia
    'Saudia Arabia', 'Yemen', 'Kenya', 'Djibouti', 'Sudan', 'Addis Ababa central market', 'South Africa', 'Dubai',
    # Ghana
    'Lake Volta', 'Lagos', 'Lebanon', 'Qatar', 'Lome', 'Paga', 'Noe',
    # India
    'Delhi', 'Mumbai', 'Kolkata', 'Pune', 'Gulf Country',
    # India Network
    'Delhi', 'GB Road', 'Gulf Country',
    # Indonesia
    'Papua', 'Malaysia', 'Saudi Arabia', 'Saudia Arabia', 'Middle East',
    # Kenya
    'Mombasa', 'Nairobi', 'Saudi Arabia', 'Qatar',
    # Lesotho
    'Johannesburg', 'Cape Town', 'Durban', 'Bloemfontein',
    # Liberia
    'Monrovia', 'Freetown', 'Conakry', 'Kuwait', 'Yamoussoukro', 'Abidjan',
    # Milawi
    'South Africa', 'Mozambique', 'Zambia', 'Blantyre', 'Lilongwe', 'Mzimba', 'Kasungu',
    # Mozambique
    'Johannesburg, South Africa', 'Eswatini', 'Dar es Salaam, Tanzania', 'Beira Port, Mozambique', 'Maputo, Mozambique'
    # Namibia
                                                                                                   'Nairobi',
    'Johannesburg', 'Lagos', 'Istanbul', 'London',
    # Nepal
    'UAE', 'Gulf Country', 'Qatar', 'Malaysia', 'Kuwait', 'Saudi Arabia', 'Jordan', 'Poland', 'South Korea', 'Turkey',
    # Rwanda
    'Kigali', 'Kampala', 'Kenya', 'Oman', 'Kigali', 'Kampala', 'Kenya', 'Oman',
    # Sierra Leone
    'Freetown', 'Kuwait', 'Conakry',
    # South Africa
    'Middle East', 'Ireland', 'South America', 'North America',
    # Tanzania
    'Dar es Salaam', 'Zanzibar', 'Johannesburg, SA', 'Oman', 'UAE',
    # Uganda
    'Kampala', 'Busia', 'Dubai', 'Nairobi',
    # Zambia
    'Johannesburg, South Africa', 'Chinotimba, Zimbabwe', 'Windhoek, Namibia', 'Dubai, UAE', 'Turkey, Europe',
    # Zimbabwe
    'South Africa', 'Mozambique', 'Harare'
]


def field_has_data(field_value):
    if field_value is None or field_value == '' or field_value == '-':
        result = False
    else:
        result = True
    return result


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('country', nargs='+', type=str)
        parser.add_argument('from_form', nargs='+', type=str)
        parser.add_argument('to_form', nargs='+', type=str)

    def update_forms(self, country, from_form, to_form):
        stations = from_form.stations.filter(operating_country=country)
        for station in stations:
            to_form.stations.add(station)
        for station in stations:
            from_form.stations.remove(station)

    def migrate_pvfCommon202408(self, country, from_form, to_form):
        print('Begin migration for', country.name)
        pvfs = VdfCommon.objects.filter(station__operating_country=country)
        for pvf in pvfs:
            modified = False
            if pvf.share_gospel_film or pvf.share_gospel_tract or pvf.share_gospel_oral or pvf.share_gospel_other:
                pvf.share_gospel_resouce = True
                modified = True

            if pvf.how_pv_released == 'Someone came to pick the PV up from the station/shelter':
                pvf.how_pv_released = 'Someone came to station/shelter to pick up the PV'
                modified = True

            if pvf.overnight_lodging == 'Yes':
                pvf.overnight_lodging = 'True'
                modified = True
            elif pvf.overnight_lodging is not None:
                pvf.overnight_lodging = 'False'
                modified = True

            if modified:
                pvf.save()

        self.update_forms(country, from_form, to_form)

    def migrate_lfCommon202409(self, country, from_form, to_form):
        lfs = LocationForm.objects.filter(station__operating_country=country)
        for lf in lfs:
            lf_modified = False
            description_match = False

            for info in lf.locationinformation_set.all():
                info_modified = False
                merge_description = False
                if not description_match:
                    # First info where description matches merged description
                    # if description in info is updated then update merged description
                    description_match = info.description == lf.merged_description
                    merge_description = description_match

                # Append descriptive fields not in the new version to the description field
                for field_name in ['location_in_town', 'color', 'number_of_levels', 'nearby_landmarks']:
                    value = getattr(info, field_name)
                    if field_has_data(value):
                        info_modified = True
                        if field_has_data(info.description):
                            info.description = info.description + '\n' + field_name + ':' + value
                        else:
                            info.description = field_name + ':' + value

                if merge_description and info_modified:
                    lf.merge_description = info.description
                    lf_modified = True

                if field_has_data(info.suspects_associative):
                    info.suspects_associative = info.suspects_associative.replace(';', ', ')
                    info_modified = True
                if field_has_data(info.persons_in_charge):
                    info_modified = True
                    if field_has_data(info.suspects_associative):
                        info.suspects_associative = (info.suspects_associative + '\nPerson in charge:' +
                                                     info.persons_in_charge.replace(';', ', '))
                    else:
                        info.suspects_associative = 'Person in charge:' + info.persons_in_charge.replace(';', ', ')
                if field_has_data(info.pvs_visited):
                    info.pvs_visited = info.pvs_visited.replace(';', ', ')
                    info_modified = True

                if info_modified:
                    info.save()

            if lf_modified:
                lf.save()

        self.update_forms(country, from_form, to_form)

    def add_checkbox_group(self, existing, new_value):
        if existing is None or existing == '':
            return new_value
        else:
            return existing + ';' + new_value

    def migrate_sfCommon202409(self, country, from_form, to_form):
        address_none = {'value': None}
        sfs = Suspect.objects.filter(station__operating_country=country)
        for sf in sfs:
            associations = sf.suspectassociation_set.all()
            for association in associations:
                modified = False
                if association.associated_pvs is not None and len(association.associated_pvs) > 0:
                    association.associated_pvs = association.associated_pvs.replace(';', ', ')
                if association.associated_suspects is not None and len(association.associated_suspects) > 0:
                    association.associated_suspects = association.associated_suspects.replace(';', ', ')
                association.save()

            legal_list = sf.suspectlegal_set.all()
            for legal in legal_list:  # should be only one
                new_location_attempt = ''
                if legal.location_attempt is not None and len(legal.location_attempt) > 0:
                    attempt = legal.location_attempt.split(';')

                    if 'In Police Custody' in attempt:
                        new_location_attempt = self.add_checkbox_group(new_location_attempt,
                                                                       'In police custody')
                if (legal.location_last_address is not None and legal.location_last_address != address_none and
                        legal.location_last_address != ''):
                    new_location_attempt = self.add_checkbox_group(new_location_attempt, 'Last known location')
                if legal.location_unable is not None and len(legal.location_unable) > 0:
                    unable = legal.location_unable.split(';')
                    if 'Insufficient Suspect Bio Details' not in unable:
                        new_location_attempt = self.add_checkbox_group(new_location_attempt,
                                                                       'Sufficient biographical details to identify the suspect')
                legal.location_attempt = new_location_attempt

                new_police_attempt = ''
                if legal.police_attempt == 'True':
                    new_police_attempt = self.add_checkbox_group(new_police_attempt, 'Yes')
                if legal.police_unable is not None and len(legal.police_unable) > 0:
                    unable = legal.police_unable.split(';')
                    if 'No' in unable:
                        new_police_attempt = self.add_checkbox_group(new_police_attempt, "No")
                    if 'Police say not enough evidence' in unable:
                        new_location_attempt = self.add_checkbox_group(new_police_attempt,
                                                                       "Police say not enough evidence")
                legal.police_attempt = new_police_attempt
                legal.save()

                suspect_pv = SuspectLegalPv()
                suspect_pv.suspect = sf
                suspect_pv.incident = legal.incident
                suspect_pv.pv_name = "Unspecified"
                if legal.pv_attempt is not None and len(legal.pv_attempt) > 0:
                    suspect_pv.willing_to_file = self.add_checkbox_group(suspect_pv.willing_to_file, 'Yes, willing')
                if legal.pv_unable is not None:
                    unable = legal.pv_unable.split(';')
                    if 'No' in unable:
                        suspect_pv.willing_to_file = self.add_checkbox_group(suspect_pv.willing_to_file,
                                                                             'Not willing to file a case at all')
                    if "Couldn't reestablish contact with PV" in unable:
                        suspect_pv.willing_to_file = self.add_checkbox_group(suspect_pv.willing_to_file,
                                                                             "Couldn’t establish contact with PV")
                    if "PV afraid for reputation" in unable:
                        suspect_pv.hesitation_concern = self.add_checkbox_group(suspect_pv.hesitation_concern,
                                                                                "Afraid for reputation")
                    if "PV afraid for their safety" in unable:
                        suspect_pv.hesitation_concern = self.add_checkbox_group(suspect_pv.hesitation_concern,
                                                                                "Afraid for their safety")
                    if "PVs don't believe they were being trafficked" in unable:
                        suspect_pv.hesitation_concern = self.add_checkbox_group(suspect_pv.hesitation_concern,
                                                                                "Don’t believe they were being trafficked")
                    if "PV family not willing" in unable:
                        suspect_pv.hesitation_concern = self.add_checkbox_group(suspect_pv.hesitation_concern,
                                                                                "Family not willing")
                suspect_pv.save()

        self.update_forms(country, from_form, to_form)

    def migrate_irf2024_08(self, country, from_form, to_form):
        # map new form name to method if custom rules are needed
        # method takes base set of rules and adds custom rules
        form_custom_rules = {

        }

        # map new form name to method if custom migration is needed (other than form_custom_rules)
        # Not sure if this will be needed for any of the forms
        form_custom_migration = {

        }

        if to_form.form_name in form_custom_rules:
            # custom rules for form
            custom_rules = form_custom_rules[to_form.form_name](BASE_VULNERABLE_RULES, BASE_INDUSTRY_RULES)
            vulnerable_rules = custom_rules['vulnerable_rules']
            industry_rules = custom_rules['industry_rules']
        else:
            vulnerable_rules = BASE_VULNERABLE_RULES
            industry_rules = BASE_INDUSTRY_RULES

        # get list of categories in the new form so the QuestionLayout rows can easily be located
        categories = []
        form_categories = FormCategory.objects.filter(form=to_form)
        for form_category in form_categories:
            categories.append(form_category.category)

        # Populate field name and points associated with the question tag for each rule
        for rule in vulnerable_rules:
            storage = QuestionStorage.objects.get(question__form_tag=rule['question_tag'])
            rule['field_name'] = storage.field_name
            points = 0
            layout = QuestionLayout.objects.get(category__in=categories, question__form_tag=rule['question_tag'])
            if layout.flag_points is not None and 'points' in layout.flag_points:
                points = layout.flag_points['points']
            rule['points'] = points

        for rule in industry_rules:
            storage = QuestionStorage.objects.get(question__form_tag=rule['question_tag'])
            rule['field_name'] = storage.field_name

        # Find all IRFs to be migrated from the old form
        irfs = IrfCommon.objects.filter(station__operating_country=country, station__in=from_form.stations.all())
        for irf in irfs:
            # Migrate Vulnerable section
            interceptees = IntercepteeCommon.objects.filter(interception_record=irf, person__role='PVOT')
            most_vulnerable_points = 0
            most_vulnerable_elements = []
            # Find interceptee with the highest number of points
            for interceptee in interceptees:
                age = None
                points = 0
                elements = []
                if interceptee.person.age is not None:
                    age = interceptee.person.age
                elif interceptee.person.birthdate is not None:
                    if irf.date_of_interception > interceptee.person.birthdate:
                        age = irf.date_of_interception.year - interceptee.person.birthdate.year
                        day_with_fixed_leap_year = interceptee.person.birthdate.day
                        month = interceptee.person.birthdate.month
                        if month == 2 and day_with_fixed_leap_year == 29:
                            day_with_fixed_leap_year = 28
                        birthdate_year_of_interception = date(
                            irf.date_of_interception.year,
                            month,
                            day_with_fixed_leap_year
                        )
                        if irf.date_of_interception < birthdate_year_of_interception:
                            age -= 1

                for rule in vulnerable_rules:
                    check_rule = True
                    for conflict in rule['conflict_tags']:
                        if conflict in elements:
                            # This rule conflicts with a previously added rule
                            check_rule = False
                            break
                    if check_rule and eval(rule['logic']):
                        elements.append(rule['question_tag'])
                        points += rule['points']

                if points > most_vulnerable_points:
                    most_vulnerable_points = points
                    most_vulnerable_elements = elements

                # This is not part of the vulnerable section, but convenient to migrate while we have the interceptee
                if (age is not None and age >= 18 and interceptee.person.full_name is not None and
                        interceptee.person.full_name != ''):
                    vdfs = VdfCommon.objects.filter(vdf_number__contains=irf.irf_number,
                                                    victim__full_name=interceptee.person.full_name)
                    if len(vdfs) > 0 and vdfs[0].guardian_know_destination == 'No':
                        irf.over_18_family_doesnt_know_going = True

            # print(('>' if most_vulnerable_points >= 10 else '<') + ',' + str(most_vulnerable_points) + ',' +
            #      irf.verified_evidence_categorization + ',' + irf.irf_number + ',"' +
            #      str(most_vulnerable_elements) + '"')

            # Set value in IRF for each of the rules where the logic returned True
            for rule in vulnerable_rules:
                value = (rule['question_tag'] in most_vulnerable_elements)
                setattr(irf, rule['field_name'], value)

            # Migrate other Sections
            # set the vulnerable point total since we already needed to compute it
            irf.vulnerable_computed_total = most_vulnerable_points

            # destination field can have multiple values separated by semicolon.
            # check each value for being a known city or country for trafficking
            # assumes country/city is known for trafficking it is valid for all countries
            destinations = irf.where_going_destination.split(';')
            for destination in destinations:
                if destination in KNOWN_FOR_TRAFFICKING:
                    irf.city_or_country_known_for_trafficking = True
                    break

            # copy the destination to the destination notes.  Actual addresses will be set later
            irf.destination_notes = irf.where_going_destination

            # Added Dubai here as it appears without the country in some destinations.
            # Other cities that should be added?
            for kafala_pattern in ['saudi arabia', 'united arab emirates', 'kuwait', 'qatar', 'bahrain', 'oman',
                                   'lebanon', 'jordon', 'dubai']:
                if kafala_pattern in irf.where_going_destination.lower():
                    irf.kafala_country = True
                    break
            # Only match UAE if it is upper case
            if not irf.kafala_country and 'UAE' in irf.where_going_destination:
                irf.kafala_country = True

            # fields being set below are new - they should already be False/Null
            if irf.industry is not None and irf.industry != '':
                industry_parts = irf.industry.split(';')
                for industry_element in industry_parts:
                    industry_part = industry_element
                    for convert in CONVERT_INDUSTRY:
                        if re.search(convert['pattern'], industry_part, re.IGNORECASE):
                            industry_part = convert['value']
                            # print(industry_element, industry_part)
                            break
                    found = False
                    for rule in industry_rules:
                        if eval(rule['logic']):
                            found = True
                            setattr(irf, rule['field_name'], True)
                    if not found and industry_part in INDUSTRY_OTHER:
                        if irf.other_industry is None:
                            irf.other_industry = industry_part + ' '
                        else:
                            irf.other_industry = irf.other_industry + industry_part + ' '

            if irf.control_visa_misuse:
                irf.evade_visa_misuse = True

            if to_form.form_name in form_custom_migration:
                # custom migration for questions other than vulnerable and industry
                vulnerable_rules = form_custom_migration[to_form.form_name](irf, country, from_form, to_form)
            irf.save()

        self.update_forms(country, from_form, to_form)

    def handle(self, *args, **options):
        method_match_list = [
            {
                'pattern': '^irf.*2024_08$',
                'method': 'migrate_irf2024_08'
            }
        ]
        country_name = options['country'][0]
        from_form_name = options['from_form'][0]
        to_form_name = options['to_form'][0]

        method_name = 'migrate_' + to_form_name
        for method_match in method_match_list:
            if re.search(method_match['pattern'], to_form_name):
                method_name = method_match['method']
                break
        method = getattr(self, method_name)

        country = Country.objects.get(name=country_name)
        from_form = Form.objects.get(form_name=from_form_name)
        to_form = Form.objects.get(form_name=to_form_name)

        already_converted = to_form.stations.filter(operating_country=country)
        if len(already_converted) > 0:
            print('There are already ' + str(len(already_converted)) + ' projects in ' + country_name +
                  ' configured with form ' + to_form_name)
            print('Migration cannot proceed')
            return

        to_convert = from_form.stations.filter(operating_country=country)
        if len(to_convert) < 1:
            print('There are no projects in ' + country_name + ' configured with form ' + from_form_name)
            print('Migration cannot proceed')
            return

        with transaction.atomic():
            method(country, from_form, to_form)
