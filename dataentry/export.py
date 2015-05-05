from django.db import models
from models import BorderStation

irf_headers = [
    "IRF Number",
    "Station",
    "Date/Time of Interception",
    "Date/Time Entered into System",
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
        "Trafficker %d Name" % i,
        "Trafficker %d Gender " % i,
        "Trafficker %d Age" % i,
        "Trafficker %d District" % i,
        "Trafficker %d VDC" % i,
        "Trafficker %d Phone" % i,
        "Trafficker %d Relationship to..." % i,
    ])


def text_if_true(condition, text):
    if condition:
        return text
    else:
        return ''


def get_station_name_from_number(irf_number):
    code = irf_number[:3].upper()
    try:
        return BorderStation.objects.get(station_code=code).station_name
    except BorderStation.DoesNotExist:
        return "UNKNOWN"

def get_checkbox_group_value(instance, field_name_start):
    for field in instance._meta.fields:
        if field.name.startswith(field_name_start):
            value = getattr(instance, field.name)
            if value:
                if isinstance(field, models.BooleanField) or isinstance(field, models.NullBooleanField):
                    return field.verbose_name
    return ''

from django.utils.timezone import make_naive, localtime


def get_irf_export_rows(irfs):
    rows = []
    rows.append(irf_headers)

    for irf in irfs:
        for interceptee in irf.interceptees.all():
            # One row for each victim, with all these beginning fields duplicated for all of them

            # If this is a trafficker, don't put them on their own row, put them at the end
            if interceptee.kind == 't':
                continue

            row = []

            date_interception = localtime(irf.date_time_of_interception)
            date_entered = localtime(irf.date_time_entered_into_system)

            row.extend([
                irf.irf_number,

                get_station_name_from_number(irf.irf_number),
                make_naive(date_interception, date_interception.tzinfo),
                make_naive(date_entered, date_entered.tzinfo),
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

                get_checkbox_group_value(irf, 'talked_to'),
                irf.talked_to_family_member_other_value,
            ])

            row.extend([
                irf.reported_total_red_flags or 0,
                irf.calculate_total_red_flags(),
            ])

            if irf.contact_noticed:
                row.append('Interception made as a result of a contact')
            elif irf.staff_noticed:
                row.append('Interception made as a result of staff')

            row.extend([
                get_checkbox_group_value(irf, 'which_contact'),
                irf.which_contact_other_value,
            ])

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
                text_if_true(irf.name_came_up_before, 'Names came up before'),
                irf.name_came_up_before_value,
                text_if_true(irf.scan_and_submit_same_day, 'Scanned and submitted same day'),
                get_checkbox_group_value(irf, 'interception_type'),
                text_if_true(irf.trafficker_taken_into_custody, 'Trafficker taken into police custody'),
            ])

            row.append(irf.trafficker_taken_into_custody)

            row.append(irf.get_how_sure_was_trafficking_display())

            if irf.has_signature:
                row.append('Form is signed')
            else:
                row.append('Form is not signed')

            row.append(interceptee.full_name or '')

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

                row.append(interceptee.full_name or '')

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

            rows.append(row)

    return rows


vif_headers = [
    "VIF Number",
    "Station",
    "Date",
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
    "Other Job Abroad",
    "Other Reason for Going Abroad",
    "2.2 Motive for Going Abroad",
    "Other Motive",
    "Destination",
    "3.1 Involvement of Manpower",
    "3.2 Recruited from Village",
    "3.3 Broker's Relation to Victim",
    "Broker's Relation Other",
    "3.4 Duration of Marriage to Broker",
    "3.5 Met Broker",
    "Met Broker Other",
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
    "Transit Free Explanation",
    "4.7 Number of Others",
    "4.8 Age of Youngest",
    "4.9 Passport Made",
    "4.10 Passport with Broker",
    "4.11 Sexual Harassment",
    "Sexual Abuse",
    "Physical Abuse",
    "Threats",
    "Denied Proper Food",
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
]

vif_pb_headers = [
    "PB%d - Relationship",
    "PB%d - Role",
    "PB%d - Gender",
    "PB%d - Name",
    "PB%d - District",
    "PB%d - VDC",
    "PB%d - Ward",
    "PB%d - Phone",
    "PB%d - Age",
    "PB%d - Height",
    "PB%d - Weight",
    "PB%d - Physical Description",
    "PB%d - Appearance",
    "PB%d - Occupation",
    "PB%d - Other Occupation",
    "PB%d - Political Affiliation",
    "PB%d - How to Locate/Contact",
    "PB%d - Interviewer Believes",
    "PB%d - Victim Believes",
    "PB%d - Association with Locations",
]
vif_lb_headers = [
    "LB%d - Place",
    "LB%d - Type of Place",

    "LB%d - VDC",
    "LB%d - District",
    "LB%d - Phone",

    "LB%d - Signboard",
    "LB%d - Location in Town",
    "LB%d - Color",

    "LB%d - Levels",
    "LB%d - Compound Wall",
    "LB%d - Roof Color",

    "LB%d - Gate Color",
    "LB%d - Person in Charge",
    "LB%d - Roof Type",

    "LB%d - Nearby Landmarks",
    "LB%d - Nearby Signboards",
    "LB%d - Other",

    "LB%d - Interviewer Believes",
    "LB%d - Victim Believes",
    "LB%d - Association with People",
]

for i in range(1, 9+1):
    vif_headers.extend([header % i for header in vif_pb_headers])
    if i != 9:
        vif_headers.extend([header % i for header in vif_lb_headers])


def get_victim_where_going(vif):
    if vif.victim_where_going_region_india:
        if vif.victim_where_going_india_didnt_know or vif.victim_where_going_india_other:
            return 'India'
        else:
            return get_checkbox_group_value(vif, 'victim_where_going_india')

    elif vif.victim_where_going_region_gulf:
        if vif.victim_where_going_gulf_didnt_know or vif.victim_where_going_gulf_other:
            return 'Gulf / Other'
        else:
            return get_checkbox_group_value(vif, 'victim_where_going_gulf')


def get_victim_how_expense_was_paid(vif):
    if vif.victim_how_expense_was_paid_paid_myself:
        return 'They paid the expenses themselves'
    if vif.victim_how_expense_was_paid_broker_paid_all:
        return 'Broker paid the expenses'
    if vif.victim_how_expense_was_paid_gave_money_to_broker:
        return 'They gave %s to the Broker' % vif.victim_how_expense_was_paid_amount
    if vif.victim_how_expense_was_paid_broker_gave_loan:
        return 'Broker paid %s and they have to pay them back' % vif.victim_how_expense_was_paid_amount


def get_broker_works_in_job_location(vif):
    if vif.broker_works_in_job_location_no:
        return 'Broker does not work in the same place'
    if vif.broker_works_in_job_location_yes:
        return 'Broker works in the same place'
    if vif.broker_works_in_job_location_dont_know:
        return 'Don\'t know if the broker works in the same place'


def get_victim_traveled_with_broker_companion(vif):
    if vif.victim_traveled_with_broker_companion_yes:
        return 'Traveled with a companion'
    if vif.victim_traveled_with_broker_companion_no:
        return 'Did not travel with a companion'
    if vif.victim_traveled_with_broker_companion_broker_took_me_to_border:
        return 'Broker took them to the border'


def get_money_changed_hands_broker_companion(vif):
    if vif.money_changed_hands_broker_companion_no:
        return 'Money did not change hands between either'
    if vif.money_changed_hands_broker_companion_dont_know:
        return 'Don\'t know if money changed hands'
    if vif.money_changed_hands_broker_companion_broker_gave_money:
        return 'Broker gave money to the Companion'
    if vif.money_changed_hands_broker_companion_companion_gave_money:
        return 'Companion gave money to the Broker'


def get_meeting_at_border(vif):
    if vif.meeting_at_border_yes:
        return 'Was planning to meet someone after crossing the border'
    if vif.meeting_at_border_no:
        return 'Was not planning on meeting anyone after crossing the border'
    if vif.meeting_at_border_meeting_broker:
        return 'Planning to meet Broker after crossing the border'
    if vif.meeting_at_border_meeting_companion:
        return 'Planning to meet Companion after crossing the border'


def get_victim_home_had_sexual_abuse(vif):
    if vif.victim_home_had_sexual_abuse_never:
        return 'Sexual abuse never takes place at home'
    if vif.victim_home_had_sexual_abuse_rarely:
        return 'Minor or rare sexual abuse takes place at home'
    if vif.victim_home_had_sexual_abuse_frequently:
        return 'Sever or frequent sexual abuse takes place at home'


def get_victim_home_had_physical_abuse(vif):
    if vif.victim_home_had_physical_abuse_never:
        return 'Physical abuse never takes place at home'
    if vif.victim_home_had_physical_abuse_rarely:
        return 'Minor or rare sexual abuse takes place at home'
    if vif.victim_home_had_physical_abuse_frequently:
        return 'Sever or frequent physical abuse takes place at home'


def get_victim_home_had_emotional_abuse(vif):
    if vif.victim_home_had_emotional_abuse_never:
        return 'Emotional abuse never takes place at home'
    if vif.victim_home_had_emotional_abuse_rarely:
        return 'Minor or rare emotional abuse takes place at home'
    if vif.victim_home_had_emotional_abuse_frequently:
        return 'Sever or frequent emotional abuse takes place at home'


def get_victim_guardian_drinks_alcohol(vif):
    if vif.victim_guardian_drinks_alcohol_never:
        return 'Guardian never drinks alcohol'
    if vif.victim_guardian_drinks_alcohol_occasionally:
        return 'Guardian occasionally drinks alcohol'
    if vif.victim_guardian_drinks_alcohol_all_the_time:
        return 'Guardian drinks alcohol all the time'


def get_victim_guardian_uses_drugs(vif):
    if vif.victim_guardian_uses_drugs_never:
        return 'Guardian never uses drugs'
    if vif.victim_guardian_uses_drugs_occasionally:
        return 'Guardian occasionally uses drugs'
    if vif.victim_guardian_uses_drugs_all_the_time:
        return 'Guardian uses drugs all the time'


def get_legal_action_against_traffickers(vif):
    if vif.legal_action_against_traffickers_no:
        return 'No legal action has been taken'
    if vif.legal_action_against_traffickers_fir_filed and vif.legal_action_against_traffickers_dofe_complaint:
        return 'An FIR and a DoFE complaint have both been filed'
    if vif.legal_action_against_traffickers_fir_filed:
        return 'An FIR has been filed'
    if vif.legal_action_against_traffickers_dofe_complaint:
        return 'A DoFE complaint has been filed'

def get_nullable_choice_text(value, text_true, text_false):
    if value is None:
        return ''
    if value:
        return text_true
    return text_false

def get_dependant_nullable_choice_text(value_depend, value, text_true, text_false):
    if value_depend is None:
        return ''
    if value_depend:
        return get_nullable_choice_text(value, text_true, text_false)
    return ''

def get_fir_and_dofe_values(vif):
    value = ""
    if vif.legal_action_fir_against_value != "" and vif.legal_action_dofe_against_value != "":
        value += vif.legal_action_fir_against_value + ", " + vif.legal_action_dofe_against_value
    elif vif.legal_action_fir_against_value != "" and vif.legal_action_dofe_against_value == "":
        value += vif.legal_action_fir_against_value
    elif vif.legal_action_fir_against_value == "" and vif.legal_action_dofe_against_value != "":
        value += vif.legal_action_dofe_against_value
    return value

def get_vif_export_rows(vifs):
    rows = []
    rows.append(vif_headers)

    for vif in vifs:
        row = []

        row.extend([
            vif.vif_number,
            get_station_name_from_number(vif.vif_number),

            vif.date,
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

            get_checkbox_group_value(vif, 'victim_caste'),
            vif.victim_caste_other_value,

            get_checkbox_group_value(vif, 'victim_occupation'),
            vif.victim_occupation_other_value,

            get_checkbox_group_value(vif, 'victim_marital_status'),

            get_checkbox_group_value(vif, 'victim_lives_with'),
            vif.victim_lives_with_other_value,

            vif.victim_num_in_family,

            get_checkbox_group_value(vif, 'victim_primary_guardian'),

            vif.victim_guardian_address_district,
            vif.victim_guardian_address_vdc,
            vif.victim_guardian_address_ward,
            vif.victim_guardian_phone,

            get_checkbox_group_value(vif, 'victim_parents_marital_status'),

            get_checkbox_group_value(vif, 'victim_education_level'),

            get_nullable_choice_text(
                vif.victim_is_literate,
                'Literate',
                'Illiterate'
            ),

            get_checkbox_group_value(vif, 'migration_plans'),
            vif.migration_plans_job_other_value,
            vif.migration_plans_other_value,

            get_checkbox_group_value(vif, 'primary_motivation'),
            vif.primary_motivation_other_value,

            get_victim_where_going(vif),

            get_nullable_choice_text(
                vif.manpower_involved,
                'Manpower was involved',
                'Manpower was not involved'
            ),

            'Was not recruited from village' if vif.victim_recruited_in_village else 'Was recruited from village',

            get_checkbox_group_value(vif, 'brokers_relation_to_victim'),
            vif.brokers_relation_to_victim_other_value,

            "Married to Broker for %d years and %d months" % (
                vif.victim_married_to_broker_years,
                vif.victim_married_to_broker_months
            ) if vif.victim_married_to_broker_years and vif.victim_married_to_broker_months else '',

            get_checkbox_group_value(vif, 'victim_how_met_broker'),
            vif.victim_how_met_broker_other_value,

            vif.victim_how_met_broker_mobile_explanation,

            "Known Broker for %d Years and %d Months" % (
                vif.victim_how_long_known_broker_years,
                vif.victim_how_long_known_broker_months
            ) if vif.victim_how_long_known_broker_years and vif.victim_how_long_known_broker_months else '',

            get_victim_how_expense_was_paid(vif),

            get_broker_works_in_job_location(vif),

            'Broker said they would be earning %s per month' % vif.amount_victim_would_earn if vif.amount_victim_would_earn else '',
            'Broker made similar promises to %s other(s)' % vif.number_broker_made_similar_promises_to if vif.number_broker_made_similar_promises_to else '',

            get_nullable_choice_text(
                vif.victim_first_time_crossing_border,
                'First time crossing the border',
                'Not their first time crossing the border'
            ),

            get_checkbox_group_value(vif, 'victim_primary_means_of_travel'),
            vif.victim_primary_means_of_travel_other_value,

            'Stayed somewhere in transit' if vif.victim_stayed_somewhere_between else 'Did not stay anywhere in transit',

            'Stayed for %s days starting on %s' % (
                vif.victim_how_long_stayed_between_days,
                vif.victim_how_long_stayed_between_start_date
            ) if vif.victim_how_long_stayed_between_days and vif.victim_how_long_stayed_between_start_date else '',

            'Was kept hidden' if vif.victim_was_hidden else '',
            vif.victim_was_hidden_explanation,

            'Was free to go outside' if vif.victim_was_free_to_go_out else 'Was not free to go outside',
            vif.victim_was_free_to_go_out_explanation,

            vif.how_many_others_in_situation,

            vif.others_in_situation_age_of_youngest,

            get_checkbox_group_value(vif, 'passport_made'),

            'Passport or work permit are with the Broker' if vif.victim_passport_with_broker else '',

            'Sexual Harassment' if vif.abuse_happened_sexual_harassment else '',
            'Sexual Abuse' if vif.abuse_happened_sexual_abuse else '',
            'Physical Abuse' if vif.abuse_happened_physical_abuse else '',
            'Threats' if vif.abuse_happened_threats else '',
            'Denied Proper Food' if vif.abuse_happened_denied_proper_food else '',
            'Forced to Take Drugs' if vif.abuse_happened_forced_to_take_drugs else '',

            vif.abuse_happened_by_whom,
            vif.abuse_happened_explanation,

            get_victim_traveled_with_broker_companion(vif),

            get_nullable_choice_text(
                vif.companion_with_when_intercepted,
                'Intercepted with Companion',
                'Companion was not with them at interception'
            ),
            get_nullable_choice_text(
                vif.planning_to_meet_companion_later,
                'Planning to meet Companion in India',
                'Not planning to meet Companion in India'
            ),

            get_money_changed_hands_broker_companion(vif),

            # 5. Destination & India Contact

            get_meeting_at_border(vif),

            'Know details about destination' if vif.victim_knew_details_about_destination else 'Don\'t know details about destination',

            'Knows of someone in India who sends girls overseas' if vif.other_involved_person_in_india else '',
            'Knows of a "husband trafficker" who sends girls overseas' if vif.other_involved_husband_trafficker else '',
            'Knows of a contact of the recruiter/companion who sends girls overseas' if vif.other_involved_someone_met_along_the_way else '',
            'Knows of someone involved in trafficking' if vif.other_involved_someone_involved_in_trafficking else '',
            'Knows of a place involved in trafficking' if vif.other_involved_place_involved_in_trafficking else '',

            get_nullable_choice_text(
                vif.victim_has_worked_in_sex_industry,
                'They previously worked in the sex industry',
                'They did not previously work in the sex industry',
            ),
            get_dependant_nullable_choice_text(
                vif.victim_has_worked_in_sex_industry,
                vif.victim_place_worked_involved_sending_girls_overseas,
                'The sex industry location was sending girls overseas',
                'The sex industry location was not sending girls overseas',
            ),

            get_checkbox_group_value(vif, 'awareness_before_interception'),
            get_checkbox_group_value(vif, 'attitude_towards_tiny_hands'),
            get_checkbox_group_value(vif, 'victim_heard_gospel'),
            get_checkbox_group_value(vif, 'victim_beliefs_now'),

            vif.tiny_hands_rating_border_staff,
            vif.tiny_hands_rating_shelter_staff,
            vif.tiny_hands_rating_trafficking_awareness,
            vif.tiny_hands_rating_shelter_accommodations,
            vif.how_can_we_serve_you_better,

            get_nullable_choice_text(
                vif.guardian_knew_was_travelling_to_india,
                'Guardian knew they were travelling to India',
                'Guardian didn\'t know they were travelling to India',
            ),

            get_nullable_choice_text(
                vif.family_pressured_victim,
                'Family/Guardian pressured them to accept Broker\'s offer',
                'Family/Guardian didn\'t pressure them',
            ),

            get_nullable_choice_text(
                vif.family_will_try_sending_again,
                'Think family/guardian will attempt to send them overseas again',
                'Don\'t think family/guardian will attempt to send them overseas again',
            ),

            get_nullable_choice_text(
                vif.victim_feels_safe_at_home,
                'Feels safe at home with guardian',
                'Does not feel safe at home with guardian',
            ),

            get_nullable_choice_text(
                vif.victim_wants_to_go_home,
                'Wants to go home',
                'Does not want to go home',
            ),

            get_victim_home_had_sexual_abuse(vif),
            get_victim_home_had_physical_abuse(vif),
            get_victim_home_had_emotional_abuse(vif),
            get_victim_guardian_drinks_alcohol(vif),
            get_victim_guardian_uses_drugs(vif),

            get_checkbox_group_value(vif, 'victim_family_economic_situation'),

            get_nullable_choice_text(
                vif.victim_had_suicidal_thoughts,
                'They expressed suicidal thoughts',
                'They did not express any suicidal thoughts',
            ),

            vif.reported_total_situational_alarms,
            vif.get_calculated_situational_alarms(),

            get_legal_action_against_traffickers(vif),
            get_fir_and_dofe_values(vif),

            get_checkbox_group_value(vif, 'reason_no_legal'),
            vif.reason_no_legal_interference_value,
            vif.reason_no_legal_other_value,

            get_checkbox_group_value(vif, 'interviewer_recommendation'),

            get_nullable_choice_text(
                vif.other_people_and_places_involved,
                'There are other people or places they know of involved in trafficking',
                'There are not any other people or places they know of involved in trafficking',
            ),

            'Form is signed by staff' if vif.has_signature else 'Form is not signed by staff',

            vif.case_notes,
        ])

        # Alternate pbs and lbs until they are done, filling in blank ones if needed
        pbs = list(vif.person_boxes.all())
        lbs = list(vif.location_boxes.all())

        for idx in range(max(len(pbs), len(lbs))):
            try:
                pb = pbs[idx]
                row.extend([
                    get_checkbox_group_value(pb, 'who_is_this_relationship'),
                    get_checkbox_group_value(pb, 'who_is_this_role'),
                    pb.get_gender_display(),
                    pb.name,
                    pb.address_district,
                    pb.address_vdc,
                    pb.address_ward,
                    pb.phone,
                    pb.age,
                    pb.height,
                    pb.weight,
                    get_checkbox_group_value(pb, 'physical_description'),
                    pb.appearance_other,
                    get_checkbox_group_value(pb, 'occupation'),
                    pb.occupation_other_value,
                    get_checkbox_group_value(pb, 'political_party'),
                    pb.where_spends_time,
                    get_checkbox_group_value(pb, 'interviewer_believes'),
                    get_checkbox_group_value(pb, 'victim_believes'),
                    'Associated with LB %d' % pb.associated_with_place_value if pb.associated_with_place_value is not None else '',
                ])
            except:
                row.extend(['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])

            try:
                lb = lbs[idx]
                row.extend([
                    get_checkbox_group_value(lb, 'which_place'),
                    get_checkbox_group_value(lb, 'what_kind_place'),

                    lb.vdc,
                    lb.district,
                    lb.phone,

                    lb.signboard,
                    lb.location_in_town,
                    lb.color,

                    lb.compound_wall,
                    lb.number_of_levels,
                    lb.roof_color,

                    lb.gate_color,
                    lb.person_in_charge,
                    lb.roof_type,

                    lb.nearby_landmarks,
                    lb.nearby_signboards,
                    lb.other,

                    get_checkbox_group_value(lb, 'interviewer_believes'),
                    get_checkbox_group_value(lb, 'victim_believes'),

                    'Associated with PB %d' % lb.associated_with_person_value if lb.associated_with_person_value is not None else '',
                ])
            except:
                row.extend(['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])

        rows.append(row)

    return rows
