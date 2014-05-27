BORDER_STATION_NAMES = {
    'BHW': 'Bhairahwa',
    'NPJ': 'Nepalgunj',
    'PRS': 'Nawalparasi',
    'DNG': 'Dang',
    'JNK': 'Janakpur',
    'GRG': 'Gaurigunj',
    'GLR': 'Guleria',
    'MHN': 'Mahendranagar',
    'DHD': 'Dhangadi',
    'MLW': 'Malangwa',
    'BRT': 'Biratnagar',
    'BHD': 'Bhadrapur',
    'GLC': 'Galchhi',
    'BGN': 'Birgunj',
    'MGL': 'Mugling',
    'NRG': 'Narayanghat',
    'HTD': 'Hetauda',
    'KVT': 'Kakarvitta',
    'PST': 'Pashupatinagar',
    'CND': 'Chandrauta',
    'KTM': 'Kathmandu',
    'TKP': 'Tikapur',
    'GAR': 'Gaur',
    'SLG': 'Siliguri',
    'LHN': 'Lahan',
}


irf_headers = [
    "IRF Number",
    "Station",
    "Date/Time",
    "Number of Victims",
    "Number of Traffickers",
    "Location",
    "Staff",
    "1.1 Traveling Alone ",
    "1.2 Traveling with Husband/Wife ",
    "1.3 Traveling with own brother, sister/relative",
    "2.1 Going for a Job ",
    "2.2 Going for visit / family / returning Home",
    "2.3 Going for Shopping",
    "2.4 Going to Study",
    "2.5 Going for Treatment ",
    "3.1 Appears drugged or drowsy",
    "3.2 Is meeting someone just across border",
    "3.3 Meeting someone he/she's seen in Nepal",
    "3.4 Was traveling with someone not with him/her",
    "3.5 Wife is under 18",
    "3.6 Was married in the past two weeks",
    "3.7 Was married within the past 2-8 weeks",
    "3.8 Met less than 2 weeks before eloping",
    "3.9 Met 2 - 12 weeks before eloping",
    "3.10 Caste not the same as alleged relative ",
    "3.11 Caught in a lie or contradiction",

    "3.12 Other Red Flag ",
    "3.13 Doesn't know he/she's going to India",
    "3.14 Running away from home (over 18) ",
    "3.15 Running away from home (under 18)",
    "3.16 Going to Gulf for work through India",
    "3.17 Going for job, no address in India ",
    "3.18 Going for job, no company phone number ",
    "3.19 Going for job, no appointment letter",
    "3.20 Has a valid Gulf country visa in passport",
    "3.21 Passport is with a broker",
    "3.22 Job is too good to be true ",
    "3.23 Called, not a real job ",
    "3.24 Called, could not confirm job",
    "3.25 No bags though claim to be going for a long time",
    "3.26 Shopping - stuff for overnight stay in bags ",
    "3.27 Going to study, no documentation of enrollment ",
    "3.28 Going to study, does not know school's name and location ",
    "3.29 Going to study, no phone number for school",
    "3.30 Called, not enrolled in school",
    "3.31 Reluctant to give info about treatment ",
    "3.32 Going for treatment, doesn't have medical documents ",
    "3.33 Going for treatment, fake medical documents",
    "3.34 Called doctor, no medical appointment ",
    "3.35 Doesn't know details about village ",
    "3.36 Reluctant to give info about village ",
    "3.37 Reluctant to give family info",
    "3.38 Will not give family info ",
    "3.39 Under 18, no family contact established",

    "3.40 Under 18, family doesn't know he/she's going ",
    "3.41 Under 18, family unwilling to let him/her go",
    "3.42 Over 18, family doesn't know he/she is going ",
    "3.43 Over 18, family unwilling to let him/her go",
    "Family Member Talked to",
    "Other Family Member Talked to",
    "Total Red Flag Points Listed",
    "Total Red Flag Points Calculated by Computer",
    "How Was Interception Made",
    "Who was the contact",
    "Other contact",
    "Paid the contact",
    "Amount Paid to Contact",
    "Staff who noticed",
    "Noticed they were hesitant",
    "Noticed they were nervous or afraid",
    "Noticed they were hurrying",
    "Noticed they were drugged or drowsy ",
    "Noticed they were wearing new clothes ",
    "Noticed they had dirty clothes",
    "Noticed they were carrying full bags",
    "Noticed they were wearing village dress ",
    "Noticed that they looked Indian ",
    "Noticed they had a typical village look",
    "Noticed they looked like an agent",
    "Noticed their caste was different",

    "Noticed that they looked young",
    "Noticed that they were sitting/waiting",
    "Noticed they were walking to the border ",
    "Noticed they were roaming around",
    "Noticed them exiting a vehicle",
    "Noticed them heading into a vehicle ",
    "Noticed them in a vehicle",
    "Noticed them in a rickshaw",
    "Noticed them in a cart",
    "Noticed them carrying a baby",
    "Noticed them on the phone",
    "Noticed other sign",
    "Called Subcommitte Chair",
    "Called THN to cross-check names ",
    "Names came up before",
    "Name that came up",
    "Scanned and submitted same day",
    "Type of Interception",
    "Trafficker taken into police custody",
    "Name of trafficker taken into custody",
    "How sure that it was a trafficking case ",
    "Staff signature on form ",
    "Victim Name",
    "Victim Gender",
    "Victim Age",
    "Victim District",

    "Victim VDC",
    "Victim Phone",
    "Victim Relationship to... "
]

for i in range(1, 5+1):
    irf_headers.extend([
        "Trafficker 1 Name",
        "Trafficker 1 Gender ",
        "Trafficker 1 Age",
        "Trafficker 1 District",
        "Trafficker 1 VDC",
        "Trafficker 1 Phone",
        "Trafficker 1 Relationship to...",
    ])


def text_if_true(condition, text):
    if condition:
        return text
    else:
        return ''


def get_station_name_from_irf_number(irf_number):
    return BORDER_STATION_NAMES.get(irf_number, '')[:3]


def get_irf_export_rows(irfs):
    rows = []
    rows.append(irf_headers)

    for irf in irfs:
        row = []
        for interceptee in irf.interceptees.all():
            # One row for each victim, with all these beginning fields duplicated for all of them

            # If this is a trafficker, don't put them on their own row, put them at the end
            if interceptee.kind == 't':
                continue

            row.extend([
                irf.irf_number,

                get_station_name_from_irf_number(irf.irf_number),

                irf.date_time_of_interception,
                irf.number_of_victims,
                irf.number_of_traffickers,

                irf.location,
                irf.staff_name,

                text_if_true(irf.who_in_group_alone, "Traveling Alone"),
                text_if_true(irf.who_in_group_husbandwife, "Traveling with Husband/Wife"),
                text_if_true(irf.who_in_group_relative, "Traveling with own brother, sister/relative"),
                text_if_true(irf.where_going_job, "Going for a Job"),
                text_if_true(irf.where_going_visit, "Going for visit / family / returning Home"),
                text_if_true(irf.where_going_shopping, "Going for Shopping"),
                text_if_true(irf.where_going_study, "Going to Study"),
                text_if_true(irf.where_going_treatment, "Going for Treatment"),

                text_if_true(irf.drugged_or_drowsy, "Appears drugged or drowsy"),
                text_if_true(irf.meeting_someone_across_border, "Is meeting someone just across border"),
                text_if_true(irf.seen_in_last_month_in_nepal, "Meeting someone he/she's seen in Nepal"),
                text_if_true(irf.traveling_with_someone_not_with_her, "Was traveling with someone not with him/her"),
                text_if_true(irf.wife_under_18, "Wife is under 18"),
                text_if_true(irf.married_in_past_2_weeks, "Was married in the past two weeks"),
                text_if_true(irf.married_in_past_2_8_weeks, "Was married within the past 2-8 weeks"),
                text_if_true(irf.less_than_2_weeks_before_eloping, "Met less than 2 weeks before eloping"),
                text_if_true(irf.between_2_12_weeks_before_eloping, "Met 2 - 12 weeks before eloping"),
                text_if_true(irf.caste_not_same_as_relative, "Caste not the same as alleged relative"),
                text_if_true(irf.caught_in_lie, "Caught in a lie or contradiction"),

                text_if_true(irf.other_red_flag, irf.other_red_flag_value),

                text_if_true(irf.doesnt_know_going_to_india, "Doesn't know he/she's going to India"),
                text_if_true(irf.running_away_over_18, "Running away from home (over 18)"),
                text_if_true(irf.running_away_under_18, "Running away from home (under 18)"),
                text_if_true(irf.going_to_gulf_for_work, "Going to Gulf for work through India"),
                text_if_true(irf.no_address_in_india, "Going for job, no address in India"),
                text_if_true(irf.no_company_phone, "Going for job, no company phone number"),
                text_if_true(irf.no_appointment_letter, "Going for job, no appointment letter"),
                text_if_true(irf.valid_gulf_country_visa, "Has a valid Gulf country visa in passport"),
                text_if_true(irf.passport_with_broker, "Passport is with a broker"),
                text_if_true(irf.job_too_good_to_be_true, "Job is too good to be true"),
                text_if_true(irf.not_real_job, "Called, not a real job"),
                text_if_true(irf.couldnt_confirm_job, "Called, could not confirm job"),
                text_if_true(irf.no_bags_long_trip, "No bags though claim to be going for a long time"),
                text_if_true(irf.shopping_overnight_stuff_in_bags, "Shopping - stuff for overnight stay in bags"),
                text_if_true(irf.no_enrollment_docs, "Going to study, no documentation of enrollment"),
                text_if_true(irf.doesnt_know_school_name, "Going to study, does not know school's name and location"),
                text_if_true(irf.no_school_phone, "Going to study, no phone number for school"),
                text_if_true(irf.not_enrolled_in_school, "Called, not enrolled in school"),
                text_if_true(irf.reluctant_treatment_info, "Reluctant to give info about treatment"),
                text_if_true(irf.no_medical_documents, "Going for treatment, doesn't have medical documents"),
                text_if_true(irf.fake_medical_documents, "Going for treatment, fake medical documents"),
                text_if_true(irf.no_medical_appointment, "Called doctor, no medical appointment"),
                text_if_true(irf.doesnt_know_villiage_details, "Doesn't know details about village"),
                text_if_true(irf.reluctant_villiage_info, "Reluctant to give info about village"),
                text_if_true(irf.reluctant_family_info, "Reluctant to give family info"),
                text_if_true(irf.refuses_family_info, "Will not give family info"),
                text_if_true(irf.under_18_cant_contact_family, "Under 18, no family contact established"),
                text_if_true(irf.under_18_family_doesnt_know, "Under 18, family doesn't know he/she's going"),
                text_if_true(irf.under_18_family_unwilling, "Under 18, family unwilling to let him/her go"),
                text_if_true(irf.over_18_family_doesnt_know, "Over 18, family doesn't know he/she is going"),
                text_if_true(irf.over_18_family_unwilling, "Over 18, family unwilling to let him/her go"),
            ])

            # Get the first two family members marked as true, (I'm guessing there will usually only be one or two
            family_members_talked_to = []
            for field, text in [
                ('talked_to_brother', 'Own brother'),
                ('talked_to_sister', 'Own sister'),
                ('talked_to_father', 'Own father'),
                ('talked_to_mother', 'Own mother'),
                ('talked_to_grandparent', 'Own grandparent'),
                ('talked_to_aunt_uncle', 'Own aunt / uncle'),
                ('talked_to_other', irf.talked_to_other_value),
            ]:
                if getattr(irf, field):
                    family_members_talked_to.append(text)
            # But just in case add two blanks to the end
            family_members_talked_to.extend(['']*2)

            row.extend(family_members_talked_to[:2])

            row.extend([
                irf.reported_total_red_flags or 0,
                irf.calculate_total_red_flags(),
            ])

            if irf.contact_noticed:
                row.append('Interception made as a result of a contact')
            elif irf.staff_noticed:
                row.append('Interception made as a result of staff')

            contacts = []
            for field, text in [
                ('contact_hotel_owner', 'Hotel owner'),
                ('contact_rickshaw_driver', 'Rickshaw driver'),
                ('contact_taxi_driver', 'Taxi driver'),
                ('contact_bus_driver', 'Bus driver'),
                ('contact_church_member', 'Church member'),
                ('contact_other_ngo', 'Other NGO'),
                ('contact_police', 'Police'),
                ('contact_subcommittee_member', 'Subcommittee member'),
                ('contact_other_value', irf.contact_other_value),
            ]:
                if getattr(irf, field):
                    contacts.append(text)
            contacts.extend(['']*2)
            row.extend(contacts[:2])

            if irf.contact_paid:
                row.append('Paid the contact')
            else:
                row.append('')

            row.append(irf.contact_paid_how_much)

            row.append(irf.staff_who_noticed)

            row.extend([
                text_if_true(irf.noticed_hesitant, 'Noticed they were hesitant'),
                text_if_true(irf.noticed_nervous_or_afraid, 'Noticed they were nervous or afraid'),
                text_if_true(irf.noticed_hurrying, 'Noticed they were hurrying'),
                text_if_true(irf.noticed_drugged_or_drowsy, 'Noticed they were drugged or drowsy'),
                text_if_true(irf.noticed_new_clothes, 'Noticed they were wearing new clothes'),
                text_if_true(irf.noticed_dirty_clothes, 'Noticed they had dirty clothes'),
                text_if_true(irf.noticed_carrying_full_bags, 'Noticed they were carrying full bags'),
                text_if_true(irf.noticed_village_dress, 'Noticed they were wearing village dress'),
                text_if_true(irf.noticed_indian_looking, 'Noticed that they looked Indian'),
                text_if_true(irf.noticed_typical_village_look, 'Noticed they had a typical village look'),
                text_if_true(irf.noticed_looked_like_agent, 'Noticed they looked like an agent'),
                text_if_true(irf.noticed_caste_difference, 'Noticed their caste was different'),
                text_if_true(irf.noticed_young_looking, 'Noticed that they looked young'),
                text_if_true(irf.noticed_waiting_sitting, 'Noticed that they were sitting/waiting'),
                text_if_true(irf.noticed_walking_to_border, 'Noticed they were walking to the border'),
                text_if_true(irf.noticed_roaming_around, 'Noticed they were roaming around'),
                text_if_true(irf.noticed_exiting_vehicle, 'Noticed them exiting a vehicle'),
                text_if_true(irf.noticed_heading_to_vehicle, 'Noticed them heading into a vehicle'),
                text_if_true(irf.noticed_in_a_vehicle, 'Noticed them in a vehicle'),
                text_if_true(irf.noticed_in_a_rickshaw, 'Noticed them in a rickshaw'),
                text_if_true(irf.noticed_in_a_cart, 'Noticed them in a cart'),
                text_if_true(irf.noticed_carrying_a_baby, 'Noticed them carrying a baby'),
                text_if_true(irf.noticed_on_the_phone, 'Noticed them on the phone'),
                text_if_true(irf.noticed_other_sign_value, irf.noticed_other_sign_value),
                text_if_true(irf.call_subcommittee_chair, 'Called Subcommitte Chair'),
                text_if_true(irf.call_thn_to_cross_check, 'Called THN to cross-check names'),
                text_if_true(irf.name_come_up_before_yes_value, 'Names came up before'),
                text_if_true(irf.scan_and_submit_same_day, 'Scanned and submitted same day'),
                irf.get_interception_type_display(),
                text_if_true(irf.trafficker_taken_into_custody, 'Trafficker taken into police custody'),
            ])

            # TODO get name of trafficker taken into custody

            irf.get_how_sure_was_trafficking_display()

            if irf.has_signature:
                row.append('Form is signed')
            else:
                row.append('Form is not signed')

            row.append(interceptee.full_name)

            if interceptee.gender == 'm':
                row.append('Male')
            else:
                row.append('Female')

            row.extend([
                interceptee.age,
                interceptee.district,
                interceptee.vdc,
                interceptee.phone_contact,
                interceptee.relation_to,
            ])

            for i, interceptee in enumerate(irf.interceptees.all()):
                # Now list all of the traffickers but not victims
                if interceptee.kind == 'v':
                    continue

                row.extend([
                    interceptee.age,
                    interceptee.district,
                    interceptee.vdc,
                    interceptee.phone_contact,
                    interceptee.relation_to,
                ])

            rows.append(row)

    return rows



vif_headers = [
    "VIF Number",
    "Station",
    "Date/Time",
    "Number of Victims",
    "Number of Traffickers",
    "Location",
    "Interviewer",
    "Statement Read",
    "Photo Permission",
    "1.1 Name",
    "1.2 Gender",
    "1.3 District",
    "VDC",
    "Ward",
    "Phone Number",
    "1.4 Age",
    "1.5 Height",
    "1.6 Weight",
    "1.7 Caste",
    "Other Caste",
    "1.8 Occupation",
    "Other Occupation",
    "1.9 Marital Status",
    "1.10 Live With",
    "Live With Other",
    "1.11 Number of Family Members",
    "1.12 Guardian",
    "1.13 Guardian District",
    "Guardian VDC",
    "Guardian Ward",
    "Guardian Phone Number",
    "1.14 Parents' Marital Status",
    "1.15 Education Level",
    "1.16 Literacy",
    "2.1 Purpose of Going Abroad",
    "Other Reason for Going Abroad",
    "2.2 Motive for Going Abroad",
    "Other Motive",
    "Destination",
    "3.1 Involvement of Manpower",
    "3.2 Recruited from Village",
    "3.3 Broker's Relation to Victim",
    "3.4 Duration of Marriage to Broker",
    "3.5 Met Broker",
    "3.6 Explanation if by mobile",
    "3.7 Length of time known Broker",
    "3.8 How Expenses Were Paid",
    "3.9 Broker Works in Place of Job",
    "3.10 Expected Earnings",
    "3.11 Broker Promised Others",
    "4.1 First Border Crossing",
    "4.2 Primary Means of Travel",
    "Other Means of Travel",
    "4.3 Transit Stay",
    "4.4 Transit Stay Duration",
    "4.5 Transit Hide",
    "Transit Hide Explanation",
    "4.6 Transit Free",
    "4.7 Number of Others",
    "4.8 Age of Youngest",
    "4.9 Passport Made",
    "4.10 Passport with Broker",
    "4.11 Sexual Harassment",
    "Sexual Abuse",
    "Physical Abuse",
    "Threats Denied Proper Food",
    "Forced to Take Drugs",
    "Person Responsible",
    "Explanation of Abuse",
    "4.12 Traveled with Companion",
    "4.14 Intercepted with Companion",
    "4.15 Planning to Meet Companion",
    "4.16 Money Changing Hands",
    "5.1 India Meeting Arranged",
    "5.2 Desination Details",
    "5.3 India Contact Sending Girls Overseas",
    "Husband Trafficker",
    "Contact of Recruiter/Companion",
    "Known Trafficker",
    "Known Location",
    "5.4 Worked in Sex Industry",
    "5.5 Location Sending Girls Overseas",
    "6.1 Awareness",
    "6.2 Think They Would Have Been Trafficked",
    "6.3 Heard the Gospel",
    "6.4 What They Believe Now",
    "6.5 Rating of Border Staff",
    "Rating of Shelter Staff",
    "Rating of Trafficking Awareness",
    "Rating of Shelter Accommodations",
    "6.6 How Can We Better Serve You",
    "7.1 Guardian Know",
    "7.2 Family/Guardian Pressure",
    "7.3 Think Guardian Will Send Them Again",
    "7.4 Feel Safe with Guardian",
    "7.5 Want to Go Home",
    "7.6 Sexual Abuse at Home",
    "Physical Abuse at Home",
    "Emotional Abuse at Home",
    "7.7 Does Guardian Drink",
    "7.8 Gurdian Drug Use",
    "7.9 Family Economic Situation",
    "7.10 Suicidal Thoughts",
    "Total Home Situational Alarms Listed",
    "Total Home Situational Alarms Calculated",
    "8.1 Legal Action",
    "Legal Action Taken Against",
    "8.2 Reason for No Legal Action",
    "Person Interfering with Legal Action",
    "Other Reason for No Legal Action",
    "8.3 Recommendation",
    "8.4 More People or Places Involved in Trafficking",
    "Staff Signature on Form",
    "Case Notes",
    "PB1 - Relationship",
    "PB1 - Role",
    "PB1 - Gender",
    "PB1 - Name",
    "PB1 - District",
    "PB1 - VDC",
    "PB1 - Ward",
    "PB1 - Phone",
    "PB1 - Age",
    "PB1 - Height",
    "PB1 - Weight",
    "PB1 - Physical Description",
    "PB1 - Appearance",
    "PB1 - Occupation",
    "PB1 - Other Occupation",
    "PB1 - Political Affiliation",
    "PB1 - How to Locate/Contact",
    "PB1 - Interviewer Believes",
    "PB1 - Victim Believes",
    "PB1 - Association with Locations",
    "LB1 - Place",
    "LB1 - Type of Place",
    "LB1 - VDC",
    "LB1 - District",
    "LB1 - Phone",
    "LB1 - Signboard LB1 - Location in Town",
    "LB1 - Color",
    "LB1 - Levels",
    "LB1 - Compound",
    "LB1 - Wall",
    "LB1 - Roof Color",
    "LB1 - Gate Color",
    "LB1 - Person in Charge",
    "LB1 - Roof Type LB1 - Nearby Landmarks",
    "LB1 - Nearby Signboards LB1 - Other",
    "LB1 - Interviewer Believes",
    "LB1 - Victim Believes",
    "LB1 - Association with People",
]
"""
for i in range(1, 5+1):
    irf_headers.extend([
        "Trafficker 1 Name",
        "Trafficker 1 Gender ",
        "Trafficker 1 Age",
        "Trafficker 1 District",
        "Trafficker 1 VDC",
        "Trafficker 1 Phone",
        "Trafficker 1 Relationship to...",
    ])
"""


def get_vif_export_rows(vifs):
    rows = []
    rows.append(vif_headers)

    for vif in vifs:
        row = []

        row.extend([
            vif.vif_number,
            get_station_name_from_irf_number(vif.vif_number),

            vif.date_time,
            vif.number_of_victims,
            vif.number_of_traffickers,

            vif.location,
            vif.interviewer,

            text_if_true(vif.statement_read_before_beginning, "Statement was read to the participant"),
            text_if_true(vif.permission_to_use_photograph, "Permission was given to use photo"),

            vif.victim_name,
            vif.victim_gender,
            vif.victim_address_district,
            vif.victim_address_vdc,
            vif.victim_address_ward,
            vif.victim_phone,
            vif.victim_age,
            vif.victim_height,
            vif.victim_weight,
            vif.get_victim_caste_display(),
        ])
        if vif.victim_occupation_other_value:
            row.append(vif.victim_occupation_other_value)
        else:
            row.append(vif.get_victim_occupation_display())

        # Make this a multiselect
        if vif.victim_occupation_other_value:
            row.append(vif.victim_occupation_other_value)
        else:
            row.append(vif.get_victim_occupation_display())

        row.append(vif.get_victim_marital_status_display())

        lives_with = []
        for field, text in [
            ('victim_lives_with_own_parents',     'Own Parent(s)'),
            ('victim_lives_with_husband',         'Husband'),
            ('victim_lives_with_husbands_family', 'Husband\'s family'),
            ('victim_lives_with_friends',         'Friends'),
            ('victim_lives_with_alone',           'Alone'),
            ('victim_lives_with_other_relative',  'Other Relative'),
            ('victim_lives_with_other',           vif.victim_lives_with_other_value),
        ]:
            if getattr(vif, field):
                lives_with.append(text)
        lives_with.extend(['']*2)
        row.extend(lives_with[:2])

        row.extend([
            vif.victim_num_in_family,
            vif.get_victim_primary_guardian_display(),
            vif.victim_guardian_address_district,
            vif.victim_guardian_address_vdc,
            vif.victim_guardian_address_ward,
            vif.victim_guardian_phone,
            vif.get_victim_parents_marital_status_display(),
            vif.get_victim_education_level_display(),
        ])

        if vif.victim_is_literate:
            row.append('Literate')
        else:
            row.append('Illiterate')

        migration_plans = []
        for field, text in [
            ('migration_plans_education',               'Education'),
            ('migration_plans_travel_tour',             'Travel / Tour'),
            ('migration_plans_shopping',                'Shopping'),
            ('migration_plans_eloping',                 'Eloping'),
            ('migration_plans_arranged_marriage',       'Arranged Marriage'),
            ('migration_plans_meet_own_family',         'Meet your own family'),
            ('migration_plans_visit_brokers_home',      'Visit broker\'s home'),
            ('migration_plans_medical_treatment',       'Medical treatment'),
            ('migration_plans_job_broker_did_not_say',  'Job - Broker did not say what job'),
            ('migration_plans_job_baby_care',           'Job - Baby Care'),
            ('migration_plans_job_factory',             'Job - Factory'),
            ('migration_plans_job_hotel',               'Job - Hotel'),
            ('migration_plans_job_shop',                'Job - Shop'),
            ('migration_plans_job_laborer',             'Job - Laborer'),
            ('migration_plans_job_brothel',             'Job - Brothel'),
            ('migration_plans_job_household',           'Job - Household'),
            ('migration_plans_job_other',               vif.migration_plans_job_value),
            ('migration_plans_other',                   vif.migration_plans_other_value),
        ]:
            if getattr(vif, field):
                migration_plans.append(text)
        migration_plans.extend(['']*2)
        row.extend(migration_plans[:2])

        primary_motivations = []
        for field, text in [
            ('primary_motivation_support_myself', 'Support myself'),
            ('primary_motivation_support_family', 'Support family'),
            ('primary_motivation_personal_debt', 'Personal Debt'),
            ('primary_motivation_family_debt', 'Family Debt'),
            ('primary_motivation_love_marriage', 'Love / Marriage'),
            ('primary_motivation_bad_home_marriage', 'Bad home / marriage'),
            ('primary_motivation_get_an_education', 'Get an education'),
            ('primary_motivation_tour_travel', 'Tour / Travel'),
            ('primary_motivation_didnt_know', 'Didn\'t know I was going abroad'),
            ('primary_motivation_other', vif.primary_motivation_other_value),
        ]:
            if getattr(vif, field):
                primary_motivations.append(text)
        primary_motivations.extend(['']*2)
        row.extend(primary_motivations[:2])

        where_going = vif.get_victim_where_going_region_display() + ' '
        if vif.victim_where_going_other_gulf_value:
            where_going += vif.victim_where_going_other_gulf_value
        elif vif.victim_where_going_other_india_value:
            where_going += vif.victim_where_going_other_india_value
        else:
            where_going += vif.get_victim_where_going_display()
        row.append(where_going)
        if vif.manpower_involved:
            row.append('Manpower was involved')
        else:
            row.append('Manpower was not involved')

        if vif.victim_recruited_in_village:
            row.append('Was not recruited from village')
        else:
            row.append('Was recruited from village')

        if vif.brokers_relation_to_victim_other_value:
            row.append(vif.brokers_relation_to_victim_other_value)
        else:
            row.append(vif.get_brokers_relation_to_victim_display())

        if vif.victim_married_to_broker_years and vif.victim_married_to_broker_months:
            row.append("Married to Broker for %d years and %d months" % (
                vif.victim_married_to_broker_years,
                vif.victim_married_to_broker_months
            ))
        else:
            row.append('')

        if vif.victim_how_met_broker_other_value:
            row.append(vif.victim_how_met_broker_other_value)
        else:
            row.append(vif.get_victim_how_met_broker_display())

        row.append(vif.victim_how_met_broker_mobile_explanation)

        if vif.victim_how_long_known_broker_years and vif.victim_how_long_known_broker_months:
            row.append("Known Broker for %d Years and %d Months" % (
                vif.victim_how_long_known_broker_years,
                vif.victim_how_long_known_broker_months
            ))

        if vif.victim_how_expense_was_paid == 'i-paid-myself':
            row.append('They paid the expenses themselves')
        if vif.victim_how_expense_was_paid == 'broker-paid':
            row.append('Broker paid the expenses')
        if vif.victim_how_expense_was_paid == 'gave-money-to-broker':
            row.append('They gave %s to the Broker' % vif.victim_how_expense_was_paid_amount)
        if vif.victim_how_expense_was_paid == 'broker-paid-and-must-repay':
            row.append('Broker paid %s and they have to pay them back' % vif.victim_how_expense_was_paid_amount)




        







        rows.append(row)




        continue

    
    
    
    
    
    
    




        # Get the first two family members marked as true, (I'm guessing there will usually only be one or two
        family_members_talked_to = []
        for field, text in [
            ('talked_to_brother', 'Own brother'),
            ('talked_to_sister', 'Own sister'),
            ('talked_to_father', 'Own father'),
            ('talked_to_mother', 'Own mother'),
            ('talked_to_grandparent', 'Own grandparent'),
            ('talked_to_aunt_uncle', 'Own aunt / uncle'),
            ('talked_to_other', vif.talked_to_other_value),
        ]:
            if getattr(vif, field):
                family_members_talked_to.append(text)
        # But just in case add two blanks to the end
        family_members_talked_to.extend(['']*2)

        row.extend(family_members_talked_to[:2])

        row.extend([
            vif.reported_total_red_flags or 0,
            vif.calculate_total_red_flags(),
        ])

        if vif.contact_noticed:
            row.append('Interception made as a result of a contact')
        elif vif.staff_noticed:
            row.append('Interception made as a result of staff')

        contacts = []
        for field, text in [
            ('contact_hotel_owner', 'Hotel owner'),
            ('contact_rickshaw_driver', 'Rickshaw driver'),
            ('contact_taxi_driver', 'Taxi driver'),
            ('contact_bus_driver', 'Bus driver'),
            ('contact_church_member', 'Church member'),
            ('contact_other_ngo', 'Other NGO'),
            ('contact_police', 'Police'),
            ('contact_subcommittee_member', 'Subcommittee member'),
            ('contact_other_value', vif.contact_other_value),
        ]:
            if getattr(vif, field):
                contacts.append(text)
        contacts.extend(['']*2)
        row.extend(contacts[:2])

        if vif.contact_paid:
            row.append('Paid the contact')
        else:
            row.append('')

        row.append(vif.contact_paid_how_much)

        row.append(vif.staff_who_noticed)

        row.extend([
            text_if_true(vif.noticed_hesitant, 'Noticed they were hesitant'),
            text_if_true(vif.noticed_nervous_or_afraid, 'Noticed they were nervous or afraid'),
            text_if_true(vif.noticed_hurrying, 'Noticed they were hurrying'),
            text_if_true(vif.noticed_drugged_or_drowsy, 'Noticed they were drugged or drowsy'),
            text_if_true(vif.noticed_new_clothes, 'Noticed they were wearing new clothes'),
            text_if_true(vif.noticed_dirty_clothes, 'Noticed they had dirty clothes'),
            text_if_true(vif.noticed_carrying_full_bags, 'Noticed they were carrying full bags'),
            text_if_true(vif.noticed_village_dress, 'Noticed they were wearing village dress'),
            text_if_true(vif.noticed_indian_looking, 'Noticed that they looked Indian'),
            text_if_true(vif.noticed_typical_village_look, 'Noticed they had a typical village look'),
            text_if_true(vif.noticed_looked_like_agent, 'Noticed they looked like an agent'),
            text_if_true(vif.noticed_caste_difference, 'Noticed their caste was different'),
            text_if_true(vif.noticed_young_looking, 'Noticed that they looked young'),
            text_if_true(vif.noticed_waiting_sitting, 'Noticed that they were sitting/waiting'),
            text_if_true(vif.noticed_walking_to_border, 'Noticed they were walking to the border'),
            text_if_true(vif.noticed_roaming_around, 'Noticed they were roaming around'),
            text_if_true(vif.noticed_exiting_vehicle, 'Noticed them exiting a vehicle'),
            text_if_true(vif.noticed_heading_to_vehicle, 'Noticed them heading into a vehicle'),
            text_if_true(vif.noticed_in_a_vehicle, 'Noticed them in a vehicle'),
            text_if_true(vif.noticed_in_a_rickshaw, 'Noticed them in a rickshaw'),
            text_if_true(vif.noticed_in_a_cart, 'Noticed them in a cart'),
            text_if_true(vif.noticed_carrying_a_baby, 'Noticed them carrying a baby'),
            text_if_true(vif.noticed_on_the_phone, 'Noticed them on the phone'),
            text_if_true(vif.noticed_other_sign_value, vif.noticed_other_sign_value),
            text_if_true(vif.call_subcommittee_chair, 'Called Subcommitte Chair'),
            text_if_true(vif.call_thn_to_cross_check, 'Called THN to cross-check names'),
            text_if_true(vif.name_come_up_before_yes_value, 'Names came up before'),
            text_if_true(vif.scan_and_submit_same_day, 'Scanned and submitted same day'),
            vif.get_interception_type_display(),
            text_if_true(vif.trafficker_taken_into_custody, 'Trafficker taken into police custody'),
        ])

        # TODO get name of trafficker taken into custody

        vif.get_how_sure_was_trafficking_display()

        if vif.has_signature:
            row.append('Form is signed')
        else:
            row.append('Form is not signed')

        row.append(interceptee.full_name)

        if interceptee.gender == 'm':
            row.append('Male')
        else:
            row.append('Female')

        row.extend([
            interceptee.age,
            interceptee.district,
            interceptee.vdc,
            interceptee.phone_contact,
            interceptee.relation_to,
        ])

        for i, interceptee in enumerate(vif.interceptees.all()):
            # Now list all of the traffickers but not victims
            if interceptee.kind == 'v':
                continue

            row.extend([
                interceptee.age,
                interceptee.district,
                interceptee.vdc,
                interceptee.phone_contact,
                interceptee.relation_to,
            ])


    return rows

