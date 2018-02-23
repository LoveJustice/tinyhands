
from django.db import transaction
from dataentry.models import Person
from dataentry.models import Interceptee
from dataentry.models import InterceptionRecord
from accounts.models import Account
from django.conf import settings

import traceback
import logging

from .field_types import Address1CsvField
from .field_types import Address2CsvField
from .field_types import BooleanCsvField
from .field_types import BooleanValuePairCsv
from .field_types import BorderStationExportOnlyCsv
from .field_types import CopyCsvField
from .field_types import DateCsvField
from .field_types import DateTimeCsvField
from .field_types import FunctionValueExportOnlyCsv
from .field_types import GroupBooleanCsv
from .field_types import MapFieldCsv
from .field_types import MapValueCsvField

from .field_types import no_translation

from .google_sheet_names import spreadsheet_header_from_export_header

logger = logging.getLogger(__name__);        

inv_how_sure = {}
for tup in InterceptionRecord.HOW_SURE_TRAFFICKING_CHOICES:
    inv_how_sure[tup[1]] = tup[0]

irf_data = [
    CopyCsvField("irf_number", "IRF Number", False),
    BorderStationExportOnlyCsv("station_name", "Station", "irf_number"),
    DateTimeCsvField("date_time_of_interception", "Date/Time of Interception"),
    DateTimeCsvField("date_time_entered_into_system", "Date/Time Entered into System"),
    CopyCsvField("number_of_victims", "Number of Victims", False),
    CopyCsvField("number_of_traffickers", "Number of Traffickers", True),
    CopyCsvField("location", "Location", False),
    CopyCsvField("staff_name", "Staff", False),

    BooleanCsvField("who_in_group_alone", "1.1 Traveling Alone", "Traveling Alone", ""),
    BooleanCsvField("who_in_group_husbandwife", "1.2 Traveling with Husband/Wife",
            "Traveling with Husband/Wife", ""),
    BooleanCsvField("who_in_group_relative", "1.3 Traveling with own brother, sister/relative",
            "Traveling with own brother, sister/relative", ""),
    BooleanCsvField("where_going_job", "2.1 Going for a Job", "Going for a Job", ""),
    BooleanCsvField("where_going_visit", "2.2 Going for visit / family / returning Home",
            "Going for visit / family / returning Home", ""),
    BooleanCsvField("where_going_shopping", "2.3 Going for Shopping", "Going for Shopping", ""),
    BooleanCsvField("where_going_study", "2.4 Going to Study","Going to Study", ""),
    BooleanCsvField("where_going_treatment", "2.5 Going for Treatment", "Going for Treatment", ""),

    BooleanCsvField("drugged_or_drowsy", "3.1 Appears drugged or drowsy", "Appears drugged or drowsy", ""),
    BooleanCsvField("wife_under_18", "3.2 Wife is under 18", "Wife is under 18", ""),
    BooleanCsvField("meeting_someone_across_border", "3.3 Is meeting someone just across border",
            "Is meeting someone just across border", ""),
    BooleanCsvField("seen_in_last_month_in_nepal", "3.4 Meeting someone he/she's seen in Nepal",
            "Meeting someone he/she's seen in Nepal", ""),
    BooleanCsvField("traveling_with_someone_not_with_her", "3.5 Was traveling with someone not with him/her",
            "Was traveling with someone not with him/her", ""),

    BooleanCsvField("married_in_past_2_weeks", "3.6 Was married in the past two weeks",
            "Was married in the past two weeks", ""),
    BooleanCsvField("married_in_past_2_8_weeks", "3.7 Was married within the past 2-8 weeks",
            "Was married within the past 2-8 weeks", ""),
    BooleanCsvField("less_than_2_weeks_before_eloping", "3.8 Met less than 2 weeks before eloping",
            "Met less than 2 weeks before eloping", ""),
    BooleanCsvField("between_2_12_weeks_before_eloping", "3.9 Met 2 - 12 weeks before eloping",
            "Met 2 - 12 weeks before eloping", ""),
    BooleanCsvField("caste_not_same_as_relative", "3.10 Caste not the same as alleged relative",
            "Caste not the same as alleged relative", ""),
    BooleanCsvField("caught_in_lie", "3.11 Caught in a lie or contradiction",
            "Caught in a lie or contradiction", ""),

    BooleanValuePairCsv("other_red_flag", "3.12 Other Red Flag", "other_red_flag_value"),

    BooleanCsvField("doesnt_know_going_to_india", "3.13 Doesn't know he/she's going to India",
            "Doesn't know he/she's going to India", ""),
    BooleanCsvField("running_away_over_18", "3.14 Running away from home (over 18)",
            "Running away from home (over 18)", ""),
    BooleanCsvField("running_away_under_18", "3.15 Running away from home (under 18)",
            "Running away from home (under 18)", ""),
    BooleanCsvField("going_to_gulf_for_work", "3.16 Going to Gulf for work through India",
            "Going to Gulf for work through India", ""),
    BooleanCsvField("no_address_in_india", "3.17 Going for job, no address in India",
            "Going for job, no address in India", ""),
    BooleanCsvField("no_company_phone", "3.18 Going for job, no company phone number",
            "Going for job, no company phone number", ""),
    BooleanCsvField("no_appointment_letter", "3.19 Going for job, no appointment letter",
            "Going for job, no appointment letter", ""),
    BooleanCsvField("valid_gulf_country_visa", "3.20 Has a valid Gulf country visa in passport",
            "Has a valid Gulf country visa in passport", ""),
    BooleanCsvField("passport_with_broker", "3.21 Passport is with a broker",
            "Passport is with a broker", ""),
    BooleanCsvField("job_too_good_to_be_true", "3.22 Job is too good to be true",
            "Job is too good to be true", ""),
    BooleanCsvField("not_real_job", "3.23 Called, not a real job",
            "Called, not a real job", ""),
    BooleanCsvField("couldnt_confirm_job", "3.24 Called, could not confirm job",
            "Called, could not confirm job", ""),
    BooleanCsvField("no_bags_long_trip",  "3.25 No bags though claim to be going for a long time",
            "No bags though claim to be going for a long time", ""),
    BooleanCsvField("shopping_overnight_stuff_in_bags",  "3.26 Shopping - stuff for overnight stay in bags",
            "Shopping - stuff for overnight stay in bags", ""),
    BooleanCsvField("no_enrollment_docs", "3.27 Going to study, no documentation of enrollment",
            "Going to study, no documentation of enrollment", ""),
    BooleanCsvField("doesnt_know_school_name", "3.28 Going to study, does not know school's name and location",
            "Going to study, does not know school's name and location", ""),
    BooleanCsvField("no_school_phone", "3.29 Going to study, no phone number for school",
            "Going to study, no phone number for school", ""),
    BooleanCsvField("not_enrolled_in_school", "3.30 Called, not enrolled in school",
            "Called, not enrolled in school", ""),
    BooleanCsvField("reluctant_treatment_info", "3.31 Reluctant to give info about treatment",
            "Reluctant to give info about treatment", ""),
    BooleanCsvField("no_medical_documents", "3.32 Going for treatment, doesn't have medical documents",
            "Going for treatment, doesn't have medical documents", ""),
    BooleanCsvField("fake_medical_documents", "3.33 Going for treatment, fake medical documents",
            "Going for treatment, fake medical documents", ""),
    BooleanCsvField("no_medical_appointment", "3.34 Called doctor, no medical appointment",
            "Called doctor, no medical appointment", ""),
    BooleanCsvField("doesnt_know_villiage_details", "3.35 Doesn't know details about village",
            "Doesn't know details about village", ""),
    BooleanCsvField("reluctant_villiage_info", "3.36 Reluctant to give info about village",
            "Reluctant to give info about village", ""),
    BooleanCsvField("reluctant_family_info", "3.37 Reluctant to give family info",
            "Reluctant to give family info", ""),
    BooleanCsvField("refuses_family_info", "3.38 Will not give family info",
            "Will not give family info", ""),
    BooleanCsvField("under_18_cant_contact_family", "3.39 Under 18, no family contact established",
            "Under 18, no family contact established", ""),
    BooleanCsvField("under_18_family_doesnt_know", "3.40 Under 18, family doesn't know he/she's going",
            "Under 18, family doesn't know he/she's going", ""),
    BooleanCsvField("under_18_family_unwilling", "3.41 Under 18, family unwilling to let him/her go",
            "Under 18, family unwilling to let him/her go", ""),
    BooleanCsvField("over_18_family_doesnt_know", "3.42 Over 18, family doesn't know he/she is going",
            "Over 18, family doesn't know he/she is going", ""),
    BooleanCsvField("over_18_family_unwilling", "3.43 Over 18, family unwilling to let him/her go",
            "Over 18, family unwilling to let him/her go", ""),

    GroupBooleanCsv("talked_to", "Family Member Talked to"),
    CopyCsvField("talked_to_family_member_other_value", "Other Family Member Talked to", False),

    CopyCsvField("reported_total_red_flags", "Total Red Flag Points Listed", True, export_null_or_blank_as="0"),
    FunctionValueExportOnlyCsv("calculate_total_red_flags", "Total Red Flag Points Calculated by Computer"),

    MapFieldCsv("Noticed", "How Was Interception Made",
            {
                "Interception made as a result of a contact": "contact_noticed",
                "Interception made as a result of staff": "staff_noticed",
                "Unknown": MapFieldCsv.set_no_field
            }),
    GroupBooleanCsv("which_contact", "Who was the contact"),
    CopyCsvField("which_contact_other_value", "Other contact", False),

    BooleanCsvField("contact_paid", "Paid the contact", "Paid the contact", ""),
    CopyCsvField("contact_paid_how_much", "Amount Paid to Contact", False),
    CopyCsvField("staff_who_noticed", "Staff who noticed", False),

    BooleanCsvField("noticed_hesitant", "Noticed they were hesitant", "Noticed they were hesitant", ""),
    BooleanCsvField("noticed_nervous_or_afraid", "Noticed they were nervous or afraid",
            "Noticed they were nervous or afraid", ""),
    BooleanCsvField("noticed_hurrying", "Noticed they were hurrying", "Noticed they were hurrying", ""),
    BooleanCsvField("noticed_drugged_or_drowsy", "Noticed they were drugged or drowsy",
            "Noticed they were drugged or drowsy", ""),
    BooleanCsvField("noticed_new_clothes", "Noticed they were wearing new clothes",
            "Noticed they were wearing new clothes", ""),
    BooleanCsvField("noticed_dirty_clothes", "Noticed they had dirty clothes",
            "Noticed they had dirty clothes", ""),
    BooleanCsvField("noticed_carrying_full_bags", "Noticed they were carrying full bags",
            "Noticed they were carrying full bags", ""),
    BooleanCsvField("noticed_village_dress", "Noticed they were wearing village dress",
            "Noticed they were wearing village dress", ""),
    BooleanCsvField("noticed_indian_looking", "Noticed that they looked Indian",
            "Noticed that they looked Indian", ""),
    BooleanCsvField("noticed_typical_village_look", "Noticed they had a typical village look",
            "Noticed they had a typical village look", ""),
    BooleanCsvField("noticed_looked_like_agent", "Noticed they looked like an agent",
            "Noticed they looked like an agent", ""),
    BooleanCsvField("noticed_caste_difference", "Noticed their caste was different",
            "Noticed their caste was different", ""),
    BooleanCsvField("noticed_young_looking", "Noticed that they looked young",
            "Noticed that they looked young", ""),
    BooleanCsvField("noticed_waiting_sitting", "Noticed that they were sitting/waiting",
            "Noticed that they were sitting/waiting", ""),
    BooleanCsvField("noticed_walking_to_border", "Noticed they were walking to the border",
            "Noticed they were walking to the border", ""),
    BooleanCsvField("noticed_roaming_around", "Noticed they were roaming around",
            "Noticed they were roaming around", ""),
    BooleanCsvField("noticed_exiting_vehicle", "Noticed them exiting a vehicle",
            "Noticed them exiting a vehicle", ""),
    BooleanCsvField("noticed_heading_to_vehicle", "Noticed them heading into a vehicle",
            "Noticed them heading into a vehicle", ""),
    BooleanCsvField("noticed_in_a_vehicle", "Noticed them in a vehicle",
            "Noticed them in a vehicle", ""),
    BooleanCsvField("noticed_in_a_rickshaw", "Noticed them in a rickshaw",
            "Noticed them in a rickshaw", ""),
    BooleanCsvField("noticed_in_a_cart", "Noticed them in a cart",
            "Noticed them in a cart", ""),
    BooleanCsvField("noticed_carrying_a_baby", "Noticed them carrying a baby",
            "Noticed them carrying a baby", ""),
    BooleanCsvField("noticed_on_the_phone", "Noticed them on the phone",
            "Noticed them on the phone", ""),

    CopyCsvField("noticed_other_sign_value", "Noticed other sign", False),

    BooleanCsvField("call_subcommittee_chair", "Called Subcommitte Chair",
            "Called Subcommitte Chair", ""),
    BooleanCsvField("call_thn_to_cross_check", "Called THN to cross-check names",
            "Called THN to cross-check names", ""),
    BooleanCsvField("name_came_up_before", "Names came up before", "Names came up before", ""),
    CopyCsvField("name_came_up_before_value", "Name that came up", True),
    BooleanCsvField("scan_and_submit_same_day", "Scanned and submitted same day",
            "Scanned and submitted same day", ""),
    GroupBooleanCsv("interception_type", "Type of Interception"),
    BooleanCsvField("trafficker_taken_into_custody", "Trafficker taken into police custody",
            "Trafficker taken into police custody", ""),
    CopyCsvField("trafficker_taken_into_custody", "Name of trafficker taken into custody", True),
    #CopyCsvField("get_how_sure_was_trafficking_display", "How sure that it was a trafficking case", True),
    
    #FunctionValueExportOnlyCsv("get_how_sure_was_trafficking_display", "How sure that it was a trafficking case"),
    MapValueCsvField("how_sure_was_trafficking", "How sure that it was a trafficking case", inv_how_sure),

    BooleanCsvField("has_signature", "Staff signature on form", "Form is signed", "Form is not signed", allow_null_or_blank_import=False),
]

additional_irf_import_data = [
    DateCsvField("date_form_received", "Date Received"),
]

interceptee_person_data = [
    CopyCsvField("full_name", "{}Name", False, allow_null_or_blank_import=False),
    MapValueCsvField('gender', "{}Gender", { "Male":"M", "Female":"F", "Unknown":"U"}, export_default="Unknown"),
    CopyCsvField("age", "{}Age", True),
    Address1CsvField("address1", "{}Address1"),
    Address2CsvField("address2", "{}Address2", "address1"),
    CopyCsvField("phone_contact", "{}Phone", False),
]

interceptee_data = []
interceptee_data.extend(interceptee_person_data)
interceptee_data.extend([CopyCsvField("relation_to", "{}Relationship to...", False)])

interceptee_import_data = [
    MapValueCsvField("kind", "{}Kind", {"v":"v", "t":"t"}),
]
interceptee_import_data.extend(interceptee_data)

irf_victim_prefix = "Victim "
irf_trafficker_prefix = "Trafficker %d "
irf_interceptee_prefix = "Interceptee %d "


def get_irf_export_rows(irfs):
    logger.debug("Enter get_irf_export_row irf count=" + str(len(irfs)))
    rows = []
    irf_headers = []
    for field in irf_data:
        irf_headers.append(field.title)

    for field in interceptee_data:
        irf_headers.append(field.title.format(irf_victim_prefix))

    for trafficker_num in range(1,5+1):
        for field in interceptee_data:
            prefix = irf_trafficker_prefix % trafficker_num
            irf_headers.append(field.title.format(prefix))

    rows.append(irf_headers)

    for irf in irfs:
        for interceptee in irf.interceptees.all():
            person = interceptee.person
            if interceptee.kind == "t":
                continue

            row = []
            # export base IRF
            for field in irf_data:
                row.append(field.exportField(irf))

            # export victim information
            for field in interceptee_data:
                if(field.title != "{}Relationship to..."):
                    row.append(field.exportField(person))
                else:
                    row.append(field.exportField(interceptee))

            # export traffickers
            for trafficker in irf.interceptees.all():
                traffick_person = trafficker.person
                if trafficker.kind == "v":
                    continue

                for field in interceptee_data:
                    if(field.title != "{}Relationship to..."):
                        row.append(field.exportField(traffick_person))
                    else:
                        row.append(field.exportField(trafficker))

            rows.append(row)
    return rows

# default the value of a field on import to the date portion of a date time field
# parameters
#    irfDict - the dictionary of IRF import values 
#    params  - the array from the default_import entry
#           position 0 is the title of the field to default
#           position 1 is this function
#           position 2 is the title of the field that contains the date time
#    name_translation - function to translate the title to the value in irfDict
def default_date_part(irfDict, params, name_translation=no_translation):
    if len(params) == 3:
        if name_translation(params[0]) not in irfDict or irfDict[name_translation(params[0])] is None:
            if name_translation(params[2]) in irfDict and irfDict[name_translation(params[2])] is not None:
                parts=irfDict[name_translation(params[2])].partition(' ')
                irfDict[name_translation(params[0])] = parts[0]
       
                
# define default values on import as array of arrays
#    inner array defines
#      position 0 - title of field to default
#      position 1 - function to invoke to determine and set default value
#      position 2... - additional values required by the function to determine the default
default_import = [
        ["Date Received", default_date_part, "Date/Time Entered into System"]
    ]

def import_irf_row(irfDict):
    errList = []
    
    entered_by = Account.objects.get(email=settings.IMPORT_ACCOUNT_EMAIL)
    
    #default column values
    for default_op in default_import:
        try:
            default_op[1](irfDict, default_op, name_translation=spreadsheet_header_from_export_header)
        except:
            logger.error ("Failed to set default for field " + default_op[0] + traceback.format_exc() )
            errList.append("Failed to set default for field " + default_op[0])
        
    
    person_titles = []
    for field in interceptee_person_data:
        person_titles.append(field.title)
    
    
    irf_nbr = irfDict[spreadsheet_header_from_export_header(irf_data[0].title)]
    if irf_nbr is None:
        errList.append("Unable to find data for IRF Number")
        return errList
    else:
        try:
            InterceptionRecord.objects.get(irf_number=irf_nbr)
            errList.append("Form already exists")
            return errList
        except:
            pass
    
    irf = InterceptionRecord()
    for field in irf_data:
        try:
            errs = field.importField(irf, irfDict, name_translation = spreadsheet_header_from_export_header)
            if errs is not None:
                errList.extend(errs)
        except:
            errList.append(field.title + ":Unexpected error - contact developer")

            
    for field in additional_irf_import_data:
        try:
            errs = field.importField(irf, irfDict, name_translation = spreadsheet_header_from_export_header)
            if errs is not None:
                errList.extend(errs)
        except:
            errList.append(field.title + ":Unexpected error - contact developer")       
     
    irf.form_entered_by = entered_by
    
    interceptee_list = []
    person_list = []
    for intercept_index in range(1, 13):
        prefix = irf_interceptee_prefix % intercept_index
        
        kind_title = interceptee_import_data[0].title.format(prefix)
        kind_title = spreadsheet_header_from_export_header(kind_title)                                                                                  
        if irfDict[kind_title] is None:
            continue

        interceptee = Interceptee()
        person = Person()
        for field in interceptee_import_data:
            try:
                if field.title in person_titles:
                    errs = field.importField(person, irfDict, prefix, 
                            name_translation = spreadsheet_header_from_export_header)
                else:
                    errs = field.importField(interceptee, irfDict, prefix, 
                            name_translation = spreadsheet_header_from_export_header)          
                if errs is not None:
                    errList.extend(errs)
            except:
                errList.append(field.title.format(prefix) + ":Unexpected error - contact developer")
        
        interceptee_list.append(interceptee)
        person_list.append(person)
        
    if len(errList) == 0:
        try:
            with transaction.atomic():
                irf.save()
                irfdb = InterceptionRecord.objects.get(id=irf.id)
                for idx in range(len(person_list)):
                    person = person_list[idx]
                    interceptee = interceptee_list[idx]
                    person.save()
                    persondb = Person.objects.get(id=person.id)
                    interceptee.interception_record = irfdb
                    interceptee.person = persondb
                    interceptee.save()
        except:
            logger.error ("Unexpected error saving IRF in database IRF Number=" + irf_nbr + traceback.format_exc() )
            errList.append("Unexpected error saving IRF in database")  
        
    return errList

def join_irf_export_rows(dictReader):
    result_dict = {}
    for row in dictReader:
        irf_number = row[irf_data[0].title]
        try:
            out_row = result_dict[irf_number]
        except:
            out_row = None
            
        if out_row is None:
            out_row = []
            
            #add columns for import status and import issues
            out_row.append("")
            out_row.append("")
            
            # export base IRF
            for field in irf_data:
                val = row[field.title]
                out_row.append(val if val is not None else "")

            # export victim information
            out_row.append('v')
            for field in interceptee_data:
                val = row[field.title.format(irf_victim_prefix)]
                out_row.append(val if val is not None else "")

            # export traffickers
            for trafficker_num in range(1,12):
                prefix = irf_trafficker_prefix % trafficker_num
                try:
                    traf_name = row[interceptee_data[0].title.format(prefix)]
                except:
                    continue
                
                if traf_name is None or traf_name == "":
                    continue
                
                out_row.append('t')             
                for field in interceptee_data:
                    val = row[field.title.format(prefix)]
                    out_row.append(val if val is not None else "")
            
            result_dict[irf_number] = out_row
        else:
            # already have an entry which should have the base IRF info and the traffickers
            # just add the victim from this row
                        # export victim information
            out_row.append('v')
            for field in interceptee_data:
                val = row[field.title.format(irf_victim_prefix)]
                out_row.append(val if val is not None else "")
                
    all_rows = []

    for key,val in result_dict.items():
        all_rows.append(val)
        
    return all_rows
