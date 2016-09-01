
from django.db import transaction
from dataentry.models import Person
from dataentry.models import VictimInterview
from dataentry.models import VictimInterviewLocationBox
from dataentry.models import VictimInterviewPersonBox
from dataentry.dataentry_signals import vif_done

from field_types import Address1CsvField
from field_types import Address2CsvField
from field_types import BooleanCsvField
from field_types import BorderStationExportOnlyCsv
from field_types import BrokerPromisesCsv
from field_types import CopyCsvField
from field_types import DateTimeCsvField
from field_types import FirDofeCsv
from field_types import FormatCsvFields
from field_types import FunctionValueExportOnlyCsv
from field_types import GroupBooleanCsv
from field_types import LegalActionCsv
from field_types import MapFieldCsv
from field_types import MapValueCsvField
from field_types import VictimHowExpensePaidCsv
from field_types import VictimWhereGoingCsv
from google_sheet_names import spreadsheet_header_from_export_header

vif_data = [
    CopyCsvField("vif_number", "VIF Number", False),
    BorderStationExportOnlyCsv("station_name","Station","vif_number"),
    CopyCsvField("date", "Date (on Form)", True),
    DateTimeCsvField("date_time_entered_into_system", "Date Entered"),

    CopyCsvField("number_of_victims", "Number of Victims", True),
    CopyCsvField("number_of_traffickers", "Number of Traffickers", True),

    CopyCsvField("location", "Location", True),
    CopyCsvField("interviewer", "Interviewer", True),

    BooleanCsvField("statement_read_before_beginning", "Statement Read", "Statement was read to the participant", ""),
    BooleanCsvField("permission_to_use_photograph", "Photo Permission", "Permission was given to use photo", ""),

    CopyCsvField("full_name", "1.1 Name", True),
    MapValueCsvField("gender", "1.2 Gender", { "male":"M", "female":"F", "Unknown":"U"}, export_default="Unknown"),

    Address1CsvField("address1", "1.3 Address1"),
    Address2CsvField("address2", "Address2", "address1"),

    CopyCsvField("victim_address_ward", "Ward", False),

    CopyCsvField("phone_contact", "Phone Number", False),
    CopyCsvField("age", "1.4 Age", True),
    CopyCsvField("victim_height", "1.5 Height", True),
    CopyCsvField("victim_weight", "1.6 Weight", True),

    GroupBooleanCsv("victim_caste", "1.7 Caste"),
    CopyCsvField("victim_caste_other_value", "Other Caste", False),

    GroupBooleanCsv("victim_occupation", "1.8 Occupation"),
    CopyCsvField("victim_occupation_other_value", "Other Occupation", False),

    GroupBooleanCsv("victim_marital_status", "1.9 Marital Status"),
    GroupBooleanCsv("victim_lives_with", "1.10 Live With"),
    CopyCsvField("victim_lives_with_other_value", "Live With Other", False),
    CopyCsvField("victim_num_in_family", "1.11 Number of Family Members", True),

    GroupBooleanCsv("victim_primary_guardian", "1.12 Guardian"),
    Address1CsvField("victim_guardian_address1", "1.13 Guardian Address1"),
    Address2CsvField("victim_guardian_address2", "Guardian Address2", "victim_guardian_address1"),
    CopyCsvField("victim_guardian_address_ward", "Guardian Ward", False),
    CopyCsvField("victim_guardian_phone", "Guardian Phone Number", False),
    GroupBooleanCsv("victim_parents_marital_status", "1.14 Parents' Marital Status"),

    GroupBooleanCsv("victim_education_level", "1.15 Education Level"),
    BooleanCsvField("victim_is_literate", "1.16 Literacy", "Literate", "Illiterate"),

    GroupBooleanCsv("migration_plans", "2.1 Purpose of Going Abroad"),
    CopyCsvField("migration_plans_job_other_value", "Other Job Abroad", False),
    CopyCsvField("migration_plans_other_value", "Other Reason for Going Abroad", False),

    GroupBooleanCsv("primary_motivation", "2.2 Motive for Going Abroad"),
    CopyCsvField("primary_motivation_other_value", "Other Motive", False),
    VictimWhereGoingCsv("victim_where_going", "Destination"),

    BooleanCsvField("manpower_involved","3.1 Involvement of Manpower",
            "Manpower was involved","Manpower was not involved"),
    BooleanCsvField("victim_recruited_in_village", "3.2 Recruited from Village",
            "Was recruited from village", "Was not recruited from village"),
    GroupBooleanCsv("brokers_relation_to_victim", "3.3 Broker's Relation to Victim"),
    CopyCsvField("brokers_relation_to_victim_other_value", "Broker's Relation Other", False),

    FormatCsvFields("victim_married_to_broker_years", "3.4 Duration of Marriage to Broker",
            "Married to Broker for {victim_married_to_broker_years} years and {victim_married_to_broker_months} months",
            "victim_married_to_broker_months"),
    GroupBooleanCsv("victim_how_met_broker", "3.5 Met Broker"),
    CopyCsvField("victim_how_met_broker_other_value", "Met Broker Other", False),
    CopyCsvField("victim_how_met_broker_mobile_explanation", "3.6 Explanation if by mobile", False),

    FormatCsvFields("victim_how_long_known_broker_years", "3.7 Length of time known Broker",
            "Known Broker for {victim_how_long_known_broker_years} Years and {victim_how_long_known_broker_months} Months",
            "victim_how_long_known_broker_months"),
    VictimHowExpensePaidCsv("victim_how_expense_was_paid", "3.8 How Expenses Were Paid"),
    MapFieldCsv("broker_works_in_job_location", "3.9 Broker Works in Place of Job",
            {
                "Broker does not work in the same place" : "broker_works_in_job_location_no",
                "Broker works in the same place" : "broker_works_in_job_location_yes",
                "Don't know if the broker works in the same place" : "broker_works_in_job_location_dont_know"
            }),


    FormatCsvFields("amount_victim_would_earn", "3.10 Expected Earnings",
                    "Broker said they would be earning {amount_victim_would_earn} per month"),
    BrokerPromisesCsv("number_broker_made_similar_promises_to", "3.11 Broker Promised Others",
              "Broker made similar promises to {number_broker_made_similar_promises_to} other(s)"),

    BooleanCsvField("victim_first_time_crossing_border", "4.1 First Border Crossing",
            "First time crossing the border", "Not their first time crossing the border"),
    GroupBooleanCsv("victim_primary_means_of_travel", "4.2 Primary Means of Travel"),
    CopyCsvField("victim_primary_means_of_travel_other_value", "Other Means of Travel", False),
    BooleanCsvField("victim_stayed_somewhere_between", "4.3 Transit Stay",
            "Stayed somewhere in transit", "Did not stay anywhere in transit"),
    FormatCsvFields("victim_how_long_stayed_between_days", "4.4 Transit Stay Duration",
              "Stayed for {victim_how_long_stayed_between_days} days starting on {victim_how_long_stayed_between_start_date}",
              "victim_how_long_stayed_between_start_date"),

    BooleanCsvField("victim_was_hidden", "4.5 Transit Hide", "Was kept hidden",""),
    CopyCsvField("victim_was_hidden_explanation", "Transit Hide Explanation", False),
    BooleanCsvField("victim_was_free_to_go_out", "4.6 Transit Free", "Was free to go outside",
            "Was not free to go outside"),
    CopyCsvField("victim_was_free_to_go_out_explanation", "Transit Free Explanation", False),

    CopyCsvField("how_many_others_in_situation", "4.7 Number of Others", True),

    CopyCsvField("others_in_situation_age_of_youngest", "4.8 Age of Youngest", True),

    GroupBooleanCsv("passport_made", "4.9 Passport Made"),

    BooleanCsvField("victim_passport_with_broker", "4.10 Passport with Broker",
            "Passport or work permit are with the Broker", ""),
    BooleanCsvField("abuse_happened_sexual_harassment","4.11 Sexual Harassment",
            "Sexual Harassment",""),
    BooleanCsvField("abuse_happened_sexual_abuse","Sexual Abuse","Sexual Abuse",""),
    BooleanCsvField("abuse_happened_physical_abuse","Physical Abuse","Physical Abuse",""),
    BooleanCsvField("abuse_happened_threats","Threats","Threats",""),
    BooleanCsvField("abuse_happened_denied_proper_food","Denied Proper Food","Denied Proper Food",""),
    BooleanCsvField("abuse_happened_forced_to_take_drugs","Forced to Take Drugs","Forced to Take Drugs",""),
    CopyCsvField("abuse_happened_by_whom", "Person Responsible", False),
    CopyCsvField("abuse_happened_explanation", "Explanation of Abuse", False),

    MapFieldCsv("victim_traveled_with_broker_companion", "4.12 Traveled with Companion",
                {
                    "Traveled with a companion" : "victim_traveled_with_broker_companion_yes",
                    "Did not travel with a companion" : "victim_traveled_with_broker_companion_no",
                    "Broker took them to the border" : "victim_traveled_with_broker_companion_broker_took_me_to_border"
                }),

    BooleanCsvField("companion_with_when_intercepted", "4.14 Intercepted with Companion",
            "Intercepted with Companion", "Companion was not with them at interception"),
    BooleanCsvField("planning_to_meet_companion_later", "4.15 Planning to Meet Companion",
            "Planning to meet Companion in India", "Not planning to meet Companion in India"),

    MapFieldCsv("money_changed_hands_broker_companion", "4.16 Money Changing Hands",
            {
                "Money did not change hands between either" : "money_changed_hands_broker_companion_no",
                "Don't know if money changed hands" : "money_changed_hands_broker_companion_dont_know",
                "Broker gave money to the Companion" : "money_changed_hands_broker_companion_broker_gave_money",
                "Companion gave money to the Broker" : "money_changed_hands_broker_companion_companion_gave_money"
            }),
    MapFieldCsv("meeting_at_border", "5.1 India Meeting Arranged",
            {
                "Was planning to meet someone after crossing the border" : "meeting_at_border_yes",
                "Was not planning on meeting anyone after crossing the border" : "meeting_at_border_no",
                "Planning to meet Broker after crossing the border" : "meeting_at_border_meeting_broker",
                "Planning to meet Companion after crossing the border" : "meeting_at_border_meeting_companion"
            }),

    BooleanCsvField("victim_knew_details_about_destination", "5.2 Desination Details",
            "Know details about destination", "Don't know details about destination"),
    BooleanCsvField("other_involved_person_in_india", "5.3 India Contact Sending Girls Overseas",
            "Knows of someone in India who sends girls overseas",""),
    BooleanCsvField("other_involved_husband_trafficker", "Husband Trafficker",
            'Knows of a "husband trafficker" who sends girls overseas',""),
    BooleanCsvField("other_involved_someone_met_along_the_way", "Contact of Recruiter/Companion",
            "Knows of a contact of the recruiter/companion who sends girls overseas",""),
    BooleanCsvField("other_involved_someone_involved_in_trafficking", "Known Trafficker",
            "Knows of someone involved in trafficking",""),
    BooleanCsvField("other_involved_place_involved_in_trafficking", "Known Location",
            "Knows of a place involved in trafficking",""),

    BooleanCsvField("victim_has_worked_in_sex_industry", "5.4 Worked in Sex Industry",
            "They previously worked in the sex industry","They did not previously work in the sex industry"),
    BooleanCsvField("victim_place_worked_involved_sending_girls_overseas",
            "5.5 Location Sending Girls Overseas",
            "The sex industry location was sending girls overseas",
            "The sex industry location was not sending girls overseas",
            "victim_has_worked_in_sex_industry"),

    GroupBooleanCsv("awareness_before_interception", "6.1 Awareness"),
    GroupBooleanCsv("attitude_towards_tiny_hands", "6.2 Think They Would Have Been Trafficked"),
    GroupBooleanCsv("victim_heard_gospel", "6.3 Heard the Gospel"),
    GroupBooleanCsv("victim_beliefs_now", "6.4 What They Believe Now"),

    CopyCsvField("tiny_hands_rating_border_staff", "6.5 Rating of Border Staff", True),
    CopyCsvField("tiny_hands_rating_shelter_staff", "Rating of Shelter Staff", True),
    CopyCsvField("tiny_hands_rating_trafficking_awareness", "Rating of Trafficking Awareness", True),
    CopyCsvField("tiny_hands_rating_shelter_accommodations", "Rating of Shelter Accommodations", True),
    CopyCsvField("how_can_we_serve_you_better", "6.6 How Can We Better Serve You", False),

    BooleanCsvField("guardian_knew_was_travelling_to_india", "7.1 Guardian Know",
            "Guardian knew they were travelling to India",
            "Guardian didn't know they were travelling to India"),
    BooleanCsvField("family_pressured_victim", "7.2 Family/Guardian Pressure",
            "Family/Guardian pressured them to accept Broker's offer",
            "Family/Guardian didn't pressure them"),
    BooleanCsvField("family_will_try_sending_again", "7.3 Think Guardian Will Send Them Again",
            "Think family/guardian will attempt to send them overseas again",
            "Don't think family/guardian will attempt to send them overseas again"),
    BooleanCsvField("victim_feels_safe_at_home", "7.4 Feel Safe with Guardian",
            "Feels safe at home with guardian", "Does not feel safe at home with guardian"),
    BooleanCsvField("victim_wants_to_go_home", "7.5 Want to Go Home",
            "Wants to go home", "Does not want to go home"),

    MapFieldCsv("victim_home_had_sexual_abuse", "7.6 Sexual Abuse at Home",
            {
                "Sexual abuse never takes place at home" : "victim_home_had_sexual_abuse_never",
                "Minor or rare sexual abuse takes place at home" : "victim_home_had_sexual_abuse_rarely",
                "Sever or frequent sexual abuse takes place at home" : "victim_home_had_sexual_abuse_frequently",
            }),
    MapFieldCsv("victim_home_had_physical_abuse", "Physical Abuse at Home",
            {
                "Physical abuse never takes place at home" : "victim_home_had_physical_abuse_never",
                "Minor or rare sexual abuse takes place at home" : "victim_home_had_physical_abuse_rarely",
                "Sever or frequent physical abuse takes place at home" : "victim_home_had_physical_abuse_frequently"
            }),
    MapFieldCsv("victim_home_had_emotional_abuse", "Emotional Abuse at Home",
            {
                "Emotional abuse never takes place at home" : "victim_home_had_emotional_abuse_never",
                "Minor or rare emotional abuse takes place at home" : "victim_home_had_emotional_abuse_rarely",
                "Sever or frequent emotional abuse takes place at home" : "victim_home_had_emotional_abuse_frequently"
            }),
    MapFieldCsv("victim_guardian_drinks_alcohol", "7.7 Does Guardian Drink",
            {
                "Guardian never drinks alcohol" : "victim_guardian_drinks_alcohol_never",
                "Guardian occasionally drinks alcohol" : "victim_guardian_drinks_alcohol_occasionally",
                "Guardian drinks alcohol all the time" : "victim_guardian_drinks_alcohol_all_the_time"
            }),
    MapFieldCsv("victim_guardian_uses_drugs", "7.8 Gurdian Drug Use",
            {
                "Guardian never uses drugs" : "victim_guardian_uses_drugs_never",
                "Guardian occasionally uses drugs" : "victim_guardian_uses_drugs_occasionally",
                "Guardian uses drugs all the time" : "victim_guardian_uses_drugs_all_the_time"
            }),

    GroupBooleanCsv("victim_family_economic_situation", "7.9 Family Economic Situation"),

    BooleanCsvField("victim_had_suicidal_thoughts", "7.10 Suicidal Thoughts",
            "They expressed suicidal thoughts", "They did not express any suicidal thoughts"),

    CopyCsvField("reported_total_situational_alarms", "Total Home Situational Alarms Listed", True),
    FunctionValueExportOnlyCsv("get_calculated_situational_alarms", "Total Home Situational Alarms Calculated"),

    LegalActionCsv("legal_action_against_traffickers", "8.1 Legal Action"),
    FirDofeCsv("fir_and_dofe_values", "Legal Action Taken Against"),

    GroupBooleanCsv("reason_no_legal", "8.2 Reason for No Legal Action"),
    CopyCsvField("reason_no_legal_interference_value", "Person Interfering with Legal Action", False),
    CopyCsvField("reason_no_legal_other_value", "Other Reason for No Legal Action", False),

    GroupBooleanCsv("interviewer_recommendation", "8.3 Recommendation"),

    BooleanCsvField("other_people_and_places_involved", "8.4 More People or Places Involved in Trafficking",
                "There are other people or places they know of involved in trafficking",
                "There are not any other people or places they know of involved in trafficking"),

    BooleanCsvField("has_signature", "Staff Signature on Form", "Form is signed by staff", "Form is not signed by staff"),

    CopyCsvField("case_notes", "Case Notes", False)
]

person_box_prefix = "PB%d - "

person_box_data = [
    GroupBooleanCsv("who_is_this_relationship", "{}Relationship"),
    GroupBooleanCsv("who_is_this_role", "{}Role"),
    CopyCsvField("address_ward", "{}Ward", False),
    CopyCsvField("height", "{}Height", True),
    CopyCsvField("weight", "{}Weight", True),
    GroupBooleanCsv("physical_description", "{}Physical Description"),
    CopyCsvField("appearance_other", "{}Appearance", False),
    GroupBooleanCsv("occupation", "{}Occupation"),
    CopyCsvField("occupation_other_value", "{}Other Occupation", False),
    GroupBooleanCsv("political_party", "{}Political Affiliation"),
    CopyCsvField("where_spends_time", "{}How to Locate/Contact", False),
    GroupBooleanCsv("interviewer_believes", "{}Interviewer Believes"),
    GroupBooleanCsv("victim_believes", "{}Victim Believes"),
    FormatCsvFields("associated_with_place_value", "{}Association with Locations",
            "Associated with LB {associated_with_place_value}")
]

person_box_person_data = [
    MapValueCsvField("gender", "{}Gender", { "Male":"M", "Female":"F", "Unknown":"U"}, export_default="Unknown"),
    CopyCsvField("full_name", "{}Name", True),
    Address1CsvField("address1", "{}Address1"),
    Address2CsvField("address2", "{}Address2", "address1"),
    CopyCsvField("phone_contact", "{}Phone", False),
    CopyCsvField("age", "{}Age", True),
]

victim_data = [
    "1.1 Name",
    "1.2 Gender",
    "1.3 Address1",
    "Address2",
    "Phone Number",
    "1.4 Age",
]

location_box_prefix = "LB%d - "

location_box_data = [
    GroupBooleanCsv("which_place", "{}Place"),
    GroupBooleanCsv("what_kind_place", "{}Type of Place"),
    Address2CsvField("address2", "{}Address2","address1"),
    Address1CsvField("address1", "{}Address1",),
    CopyCsvField("phone", "{}Phone", False),
    CopyCsvField("signboard", "{}Signboard", False),
    CopyCsvField("location_in_town", "{}Location in Town", False),
    CopyCsvField("color", "{}Color", False),
    CopyCsvField("compound_wall", "{}Compound Wall", False),
    CopyCsvField("number_of_levels", "{}Levels", False),
    CopyCsvField("roof_color", "{}Roof Color", False),
    CopyCsvField("gate_color", "{}Gate Color", False),
    CopyCsvField("person_in_charge", "{}Person in Charge", False),
    CopyCsvField("roof_type", "{}Roof Type", False),
    CopyCsvField("nearby_landmarks", "{}Nearby Landmarks", False),
    CopyCsvField("nearby_signboards", "{}Nearby Signboards", False),
    CopyCsvField("other", "{}Other", False),
    GroupBooleanCsv("interviewer_believes", "{}Interviewer Believes"),
    GroupBooleanCsv("victim_believes", "{}Victim Believes"),
    FormatCsvFields("associated_with_person_value", "{}Association with People",
            "Associated with PB {associated_with_person_value}"),
]

def get_vif_export_rows(vifs):
    rows = []

    vif_headers = []

    for field in vif_data:
        vif_headers.append(field.title)

    for i in range(1, 9+1):
        for field in person_box_person_data:
            prefix = person_box_prefix % i
            vif_headers.append(field.title.format(prefix))

        for field in person_box_data:
            prefix = person_box_prefix % i
            vif_headers.append(field.title.format(prefix))


        if i < 9:
            for field in location_box_data:
                prefix = location_box_prefix % i
                vif_headers.append(field.title.format(prefix))

    rows.append(vif_headers)


    for vif in vifs:
        person = vif.victim
        row = []

        for field in vif_data:
            if field.title in victim_data:
                row.append(field.exportField(person))
            else:
                row.append(field.exportField(vif))



        pbs = list(vif.person_boxes.all().order_by('id'))
        lbs = list(vif.location_boxes.all().order_by('id'))

        for idx in range(max(len(pbs), len(lbs))):
            if idx < len(pbs):
                pbs_instance = pbs[idx]
                person = pbs_instance.person
                for field in person_box_person_data:
                    row.append(field.exportField(person))

                for field in person_box_data:
                    row.append(field.exportField(pbs_instance))
            else:
                for field in person_box_person_data:
                    row.append("")
                for field in person_box_data:
                    row.append("")

            if idx < len(lbs):
                lbs_instance = lbs[idx]
                for field in location_box_data:
                    row.append(field.exportField(lbs_instance))
            else:
                for field in location_box_data:
                    row.append("")

        rows.append(row)

    return rows

def import_vif_row(vifDict):
    errList = []
    
    vif_nbr = vifDict[spreadsheet_header_from_export_header(vif_data[0].title)]
    if vif_nbr is None:
        errList.append("Unable to find data for VIF Number")
        return errList
    else:
        try:
            VictimInterview.objects.get(vif_number=vif_nbr)
            errList.append("VIF already exists")
            return errList
        except:
            pass
    
    person = Person()
    vif = VictimInterview()
    for field in vif_data:
        try:
            if field.title in victim_data:
                errs = field.importField(person, vifDict, "", 
                        name_translation = spreadsheet_header_from_export_header)
            else:
                errs = field.importField(vif, vifDict, "", 
                        name_translation = spreadsheet_header_from_export_header)
            if errs is not None:
                errList.extend(errs)
        except:
            errList.append(field.title + ":Unexpected error - contact developer");
            
     
    location_boxes=[]
    person_boxes=[]
    person_box_persons=[] 
    for idx in range(1,10):
        
        prefix = person_box_prefix % idx
        found = False
        for field in person_box_person_data:
            tmp = vifDict.get(spreadsheet_header_from_export_header(field.title.format(prefix)))
            if tmp is not None:
                found = True
                break
        if found:
            tmp_person = Person()
            for field in person_box_person_data:
                try:
                    errs = field.importField(tmp_person, vifDict, prefix, 
                            name_translation = spreadsheet_header_from_export_header)
                    if errs is not None:
                        errList.extend(errs)     
                except:
                    errList.append(field.title.format(prefix) + ":Unexpected error - contact developer")
            
            person_box_persons.append(tmp_person)
               
            tmp_person_box = VictimInterviewPersonBox()
            for field in person_box_data:
                try:
                    errs = field.importField(tmp_person_box, vifDict, prefix, 
                            name_translation = spreadsheet_header_from_export_header)
                    if errs is not None:
                        errList.extend(errs)
                except:
                    errList.append(field.title.format(prefix) + ":Unexpected error - contact developer")
                
            person_boxes.append(tmp_person_box)

        prefix = location_box_prefix % idx
        found = False
        for field in location_box_data:
            tmp = vifDict.get(spreadsheet_header_from_export_header(field.title.format(prefix)))
            if tmp is not None:
                found = True
                break
         
        if found: 
            tmp_location = VictimInterviewLocationBox()   
            # The order that fields are imported is not important except that Address1 fields
            # must be imported before Address2 fields
            for field in location_box_data:
                if isinstance(field, Address1CsvField):
                    try:
                        errs = field.importField(tmp_location, vifDict, prefix, 
                                name_translation = spreadsheet_header_from_export_header)
                        if errs is not None:
                            errList.extend(errs)
                    except:
                        errList.append(field.title.format(prefix) + ":Unexpected error - contact developer")
                    
            for field in location_box_data:
                if not isinstance(field, Address1CsvField):
                    try:
                        errs = field.importField(tmp_location, vifDict, prefix, 
                                name_translation = spreadsheet_header_from_export_header)
                        if errs is not None:
                            errList.extend(errs)
                    except:
                        errList.append(field.title.format(prefix) + ":Unexpected error - contact developer")
                    
            location_boxes.append(tmp_location)           
        
    if len(errList) == 0:
        try:
            with transaction.atomic():
                person.save()
                persondb = Person.objects.get(id=person.id)
                vif.victim = persondb
                vif.save()
                vifdb = VictimInterview.objects.get(id=vif.id)
                for idx in range(len(person_boxes)):
                    person_box_persons[idx].save()
                    person_box_person_db = Person.objects.get(id=person_box_persons[idx].id)
                    person_boxes[idx].victim_interview = vifdb
                    person_boxes[idx].person= person_box_person_db
                    person_boxes[idx].save()
                    
                    
                for idx in range (len(location_boxes)):
                    location_boxes[idx].victim_interview = vifdb
                    location_boxes[idx].save()
                    
            vif_done.send(sender=__file__, vif_number=vif.vif_number, irf=vif)    
        except:
            errList.append("Unexpected error saving VIF in database - contact developer")
             
        
    return errList
