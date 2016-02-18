from parse import parse
from django.db import models
from models import BorderStation
from models import Address1
from models import Address2
from django.utils.timezone import make_naive, localtime

#####################################################
# Note: import logic is not complete in this version
#####################################################

# export/import field value - no translation
class CopyCsvField:
    def __init__(self, data_name, title, use_none_for_blank, export_null_or_blank_as=""):
        self.data_name = data_name
        self.title = title
        self.use_none_for_blank = use_none_for_blank
        self.export_null_or_blank_as = export_null_or_blank_as

    def importField(self, instance, csv_map, title_prefix = None):
        if title_prefix is not None:
            column_title = self.title.format(title_prefix )
        else:
            column_title = self.title
        value = csv_map[column_title]
        if value is not None:
            if value == "" and self.use_none_for_blank:
                value = None

            setattr(instance, self.data_name, value)
        else:
            self.stderr.write("Cannot set {}", self.data_name)

    def exportField(self, instance):
        rv = getattr(instance, self.data_name)
        if rv is None or rv == "":
            rv = self.export_null_or_blank_as

        return rv

# export/import date value
class DateCsvField:
    def __init__(self, data_name, title):
        self.data_name = data_name
        self.title = title

    def importField(self, instance, csv_map, title_prefix = None):
        if title_prefix is not None:
            column_title = self.title.format(title_prefix)
        else:
            column_title = self.title
        value = csv_map[column_title]
        if value is not None:
            setattr(instance, self.data_name, value)
        else:
            self.stderr.write("No data value found for {}", self.data_name)

    def exportField(self, instance):
        value = getattr(instance, self.data_name)
        local_val = localtime(value)
        local_val = local_val.replace(microsecond=0)
        return make_naive(local_val, local_val.tzinfo)

# export text string for boolean field - one value for true alternate value for false
class BooleanCsvField:
    def __init__(self, data_name, title, true_string, false_string, depend_name = None):
        self.data_name = data_name
        self.title = title
        self.true_string = true_string
        self.false_string = false_string
        self.depend_name = depend_name

    def importField(self, instance, csv_map, title_prefix = None):
        if title_prefix is not None:
            column_title = self.title.format(title_prefix)
        else:
            column_title = self.title
        value = csv_map[column_title]
        if value is not None:
            if value == self.true_string:
                value = True
            elif value == self.false_string:
                value = True
            elif value == "":
                value = None
            else:
                self.stderr.write('boolean field: data "{}" does not match true value "{}" or false value "{}"',
                    value, self.true_string, self.false_string)
                return

            setattr(instance, self.data_name, value)
        else:
            self.stderr.write("No data value found for {}", self.data_name)

    def exportField(self, instance):
        if self.depend_name is not None:
            dep_value = getattr(instance, self.depend_name)
            if dep_value is None or dep_value == False:
                return ""

        value = getattr(instance, self.data_name)
        rv = ""
        if value is not None:
            if value:
                rv = self.true_string
            else:
                rv = self.false_string

        return rv



# export/import a single verbose name from a group of similarly named boolean fields
class GroupBooleanCsv:
    def __init__(self, data_name, title):
        self.data_name = data_name
        self.title = title

    def importField(self, instance, csv_map, title_prefix = None):
        if title_prefix is not None:
            column_title = self.title.format(title_prefix)
        else:
            column_title = self.title
        value = csv_map[column_title]
        if value is not None:
            for field in instance._meta.fields:
                if field.name.startswith(value) and (
                        isinstance(field, models.BooleanField) or isinstance(field, models.NullBooleanField)):
                    if field.verbose_name == value:
                        setattr(instance, field.name, True)
                        return

            self.stderr.write("Unable to find boolean field with verbose name {}", value)
        else:
            self.stderr.write("No data value found for {}", self.data_name)

    def exportField(self, instance):
        for field in instance._meta.fields:
            if field.name.startswith(self.data_name):
                value = getattr(instance, field.name)
                if value:
                    if isinstance(field, models.BooleanField) or isinstance(field, models.NullBooleanField):
                        return field.verbose_name
        return ""

# Export/import value that represents a pair of fields.  If the boolean field is true, the the value of
# the second field is exported
class BooleanValuePairCsv:
    def __init__(self, boolean_field_name, title, value_field_name):
        self.data_name = boolean_field_name
        self.title = title
        self.value_name = value_field_name

    def importField(self, instance, csv_map, title_prefix = None):
        if title_prefix is not None:
            column_title = self.title.format(title_prefix)
        else:
            column_title = self.title
        value = csv_map[column_title]
        if value is not None:
            if value == '':
                setattr(instance, self.data_name, False)
                setattr(instance, self.value_name, None)
            else:
                setattr(instance, self.data_name, True)
                setattr(instance, self.value_name, value)
        else:
            self.stderr.write("No data value found for {}", self.data_name)

    def exportField(self, instance):
        boolVal = getattr(instance, self.data_name)
        if boolVal:
            value = getattr(instance, self.value_name)
            if value is not None:
                return value

        return ""


# Export/import a single string from a set of boolean fields.  Map identifies the set of
# fields and the value to be exported for each
class MapFieldCsv:
    def __init__(self, data_name, title, value_to_field_map):
        self.data_name = data_name
        self.title = title
        self.value_to_field_map = value_to_field_map

    def importField(self, instance, csv_map, title_prefix = None):
        if title_prefix is not None:
            column_title = self.title.format(title_prefix)
        else:
            column_title = self.title
        value = csv_map[column_title]
        if value is not None:
            field_name = self.value_to_field_map[value]
            if field_name is not None:
                setattr(instance, field_name, True)
            else:
                self.stderr.write("No mapping to field for value {} for item", value, self.data_name)
        else:
            self.stderr.write("No data value found for {}", self.data_name)

    def exportField(self, instance):
        for key, val in self.value_to_field_map.items():
            value = getattr(instance, val)
            if value:
                return key

        return ""

# Export/import a set of fields in a single formatted string
class FormatCsvFields:
    def __init__(self, data_name, title, formatString, *additional):
        self.data_name = data_name
        self.title = title
        self.formatString = formatString
        self.additional = additional

    def importField(self, instance, csv_map, title_prefix = None):
        if title_prefix is not None:
            column_title = self.title.format(title_prefix)
        else:
            column_title = self.title
        tmp = csv_map[column_title]
        if tmp is None or tmp == "":
            return

        parse_map = tmp.parse(self.formatString)
        if len(parse_map) != len(self.additional) +1:
            # Exception
            return

        tmp_val = parse_map[self.data_name]
        if tmp_val is None:
            #Exception
            return

        instance.setattr(self.data_name, tmp_val)

        for add_name in self.additional:
            tmp_val = parse_map[add_name]
            if tmp_val is None:
                #Exception
                return
            instance.setattr(add_name, tmp_val)


    def exportField(self, instance):
        values = {}
        tmp = getattr(instance, self.data_name)
        if tmp is None:
            return ""

        values[self.data_name] = tmp
        for param in self.additional:
            tmp = getattr(instance, param)
            if tmp is None:
                return ""
            values[param] = tmp

        return self.formatString.format(**values)

# Export/import District field
class DistrictCsvField:
    def __init__(self, data_name, title):
        self.data_name = data_name
        self.title = title

    def importField(self, instance, csv_map, title_prefix = None):
        if title_prefix is not None:
            column_title = self.title.format(title_prefix)
        else:
            column_title = self.title
        value = csv_map[column_title]
        district = Address1.objects.get(name=self.data_name)
        if district is not None:
            setattr(instance, self.data_name, value)


    def exportField(self, instance):
        value = ""
        try:
            tmp = getattr(instance, self.data_name)
            if tmp is not None:
                value = tmp
        finally:
            return value

# Export/import Address2 field
class VdcCsvField:
    def __init__(self, data_name, title):
        self.data_name = data_name
        self.title = title

    def importField(self, instance, csv_map, title_prefix = None):
        if title_prefix is not None:
            column_title = self.title.format(title_prefix)
        else:
            column_title = self.title
        value = csv_map[column_title]
        district = Address2.objects.get(name=self.data_name)
        if district is not None:
            setattr(instance, self.data_name, value)


    def exportField(self, instance):
        value = ""
        try:
            tmp = getattr(instance, self.data_name)
            if tmp is not None:
                value = tmp
        finally:
            return value

# Export/import value from a field.  Map identifies the mapping from the database value
# to the export value
class MapValueCsvField:
    def __init__(self, data_name, title, value_map, export_default=""):
        self.data_name = data_name
        self.title = title
        self.value_map = value_map
        self.export_default = export_default

    def importField(self, instance, csv_map, title_prefix = None):
        if title_prefix is not None:
            column_title = self.title.format(title_prefix)
        else:
            column_title = self.title
        value = csv_map[column_title]
        if value is not None:
            mapped_value = self.value_map[value]
            if mapped_value is not None:
                setattr(instance, self.data_name, mapped_value)
            else:
                self.stderr.write("No mapping for value {} for item", value, self.data_name)
        else:
            self.stderr.write("No data value found for {}", self.data_name)

    def exportField(self, instance):
        value = getattr(instance, self.data_name)

        for key, val in self.value_map.items():
            if val == value:
                return key

        return self.export_default

# Export the value returned by a function
class FunctionValueExportOnlyCsv:
    def __init__(self, data_name, title):
        self.data_name = data_name
        self.title = title

    def importField(self, instance, csv_map, title_prefix = None):
        pass

    def exportField(self, instance):
        function = getattr(instance, self.data_name)
        if function is not None:
            return function()
        self.stderr.write("No function named {} found", self.data_name)
        return ""

# Export the border station based on a base_field (e.g. irf_number)
class BorderStationExportOnlyCsv:
    def __init__(self, data_name, title, base_field):
        self.data_name = data_name
        self.title = title
        self.base_field = base_field

    def importField(self, instance, csv_map, title_prefix = None):
        pass

    def exportField(self, instance):
        rv = "UNKNOWN"
        try:
            value = getattr(instance, self.base_field)
            if value is not None:
                code = value[:3].upper()
                rv = BorderStation.objects.get(station_code=code).station_name
        finally:
            return rv

#
# Custom classes specific to one field
#
class VictimHowExpensePaidCsv:
    def __init__(self, data_name, title):
        self.data_name = "victim_how_expense_was_paid"
        self.title = title
        self.msgs = {
                "victim_how_expense_was_paid_paid_myself":"They paid the expenses themselves",
                "victim_how_expense_was_paid_broker_paid_all":"Broker paid the expenses",
                "victim_how_expense_was_paid_gave_money_to_broker":"They gave {} to the Broker",
                "victim_how_expense_was_paid_broker_gave_loan":"Broker paid {} and they have to pay them back"
        }

    def importField(self, instance, csv_map, title_prefix = None):
        if title_prefix is not None:
            column_title = self.title.format(title_prefix)
        else:
            column_title = self.title
        value = csv_map[column_title]
        if value is not None:
            for msg in self.msgs.keys():
                fmt = self.msgs[msg]
                rv = parse(fmt, value)
                if rv is not None:
                    instance.setattr(instance, msg, True)
                    if len(rv) > 0:
                        instance.victim_how_expense_was_paid_amount = rv[0]
        else:
            self.stderr.write("No data value found for {}", self.data_name)

    def exportField(self, instance):
        for msg in self.msgs.keys():
            bool_val = getattr(instance, msg)
            if bool_val is not None:
                if bool_val:
                    fmt = self.msgs[msg]

                    return fmt.format(instance.victim_how_expense_was_paid_amount)

        return ""

class BrokerPromisesCsv(FormatCsvFields):
    def __init__(self, data_name, title, formatString):
        FormatCsvFields.__init__(self, data_name, title, formatString)

    def exportField(self, instance):
        tmp = getattr(instance, self.data_name)
        if tmp is None or tmp == 0:
            return ""

        return FormatCsvFields.exportField(self, instance)

class VictimWhereGoingCsv:
    def __init__(self, data_name, title):
        self.data_name = data_name
        self.title = title

    def importField(self, instance, csv_map, title_prefix = None):
        pass

    def exportField(self, instance):
        if instance.victim_where_going_region_india:
            if instance.victim_where_going_india_didnt_know:
                return "Unknown location in India"
            elif instance.victim_where_going_india_other:
                other_value = instance.victim_where_going_india_other_value
                if other_value is None or other_value == "":
                    return "India"
                else:
                    return other_value + ", India"
            else:
                val = self.verbose_name(instance, "victim_where_going_india", None)
                if val is None:
                    return "India"
                else:
                    return val

        elif instance.victim_where_going_region_gulf:
            if instance.victim_where_going_gulf_didnt_know:
                return "Unknown location in Gulf / Other"
            elif instance.victim_where_going_gulf_other:
                other_value = instance.victim_where_going_gulf_other_value
                if other_value is None or other_value == "":
                    return "Gulf / Other"
                else:
                    return other_value
            else:
                val = self.verbose_name(instance, 'victim_where_going_gulf', None)
                if val is None:
                    return "Gulf / Other"
                else:
                    return val

    def verbose_name(self, instance, prefix, default):
        for field in instance._meta.fields:
            if field.name.startswith(prefix):
                value = getattr(instance, field.name)
                if value:
                    if isinstance(field, models.BooleanField) or isinstance(field, models.NullBooleanField):
                        return field.verbose_name
        return default

class LegalActionCsv:
    def __init__(self, data_name, title):
        self.data_name = data_name
        self.title = title

    def importField(self, instance, csv_map, title_prefix = None):
        if title_prefix is not None:
            column_title = self.title.format(title_prefix)
        else:
            column_title = self.title
        value = csv_map[column_title]
        if value is None:
            self.stderr.write("No data value found for {}", self.data_name)
            return
        if value == "No legal action has been taken":
            instance.legal_action_against_traffickers_no = True
        elif value == "An FIR and a DoFE complaint have both been filed":
            instance.legal_action_against_traffickers_fir_filed = True
            instance.legal_action_against_traffickers_dofe_complaint = True
        elif value == "An FIR has been filed":
            instance.legal_action_against_traffickers_fir_filed = True
        elif value == "A DoFE complaint has been filed":
            instance.legal_action_against_traffickers_dofe_complaint = True

    def exportField(self, instance):
        if instance.legal_action_against_traffickers_no:
            return "No legal action has been taken"
        if instance.legal_action_against_traffickers_fir_filed and instance.legal_action_against_traffickers_dofe_complaint:
            return "An FIR and a DoFE complaint have both been filed"
        if instance.legal_action_against_traffickers_fir_filed:
            return "An FIR has been filed"
        if instance.legal_action_against_traffickers_dofe_complaint:
            return "A DoFE complaint has been filed"

class FirDofeCsv:
    def __init__(self, data_name, title):
        self.data_name = data_name
        self.title = title

    def importField(self, instance, csv_map, title_prefix = None):
        if title_prefix is not None:
            column_title = self.title.format(title_prefix)
        else:
            column_title = self.title
        value = csv_map[column_title]
        if value is None:
            self.stderr.write("No data value found for {}", self.data_name)
            return

        if value != "":
            parts = value.partition(",")
            if parts[2] != "":
                instance.legal_action_fir_against_value = parts[0]
                instance.legal_action_dofe_against_value = parts[2]
            elif instance.legal_action_against_traffickers_fir_filed:
                instance.legal_action_fir_against_value = value
            elif instance.legal_action_against_traffickers_dofe_complaint:
                instance.legal_action_dofe_against_value = value
            else:
                self.stderr.write("Value '{}' provided, but both legal action flags are false", value)


    def exportField(self, instance):
        value = ""
        if instance.legal_action_fir_against_value != "" and instance.legal_action_dofe_against_value != "":
            value += instance.legal_action_fir_against_value + ", " + instance.legal_action_dofe_against_value
        elif instance.legal_action_fir_against_value != "":
            value += instance.legal_action_fir_against_value
        elif instance.legal_action_dofe_against_value != "":
            value += instance.legal_action_dofe_against_value
        return value


irf_data = [
    CopyCsvField("irf_number", "IRF Number", False),
    BorderStationExportOnlyCsv("station_name", "Station", "irf_number"),
    DateCsvField("date_time_of_interception", "Date/Time of Interception"),
    DateCsvField("date_time_entered_into_system", "Date/Time Entered into System"),
    CopyCsvField("number_of_victims", "Number of Victims", False),
    CopyCsvField("number_of_traffickers", "Number of Traffickers", False),
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
    CopyCsvField("talked_to_family_member_other_value", "Other Family Member Talked to", True),

    CopyCsvField("reported_total_red_flags", "Total Red Flag Points Listed", True, export_null_or_blank_as="0"),
    FunctionValueExportOnlyCsv("calculate_total_red_flags", "Total Red Flag Points Calculated by Computer"),

    MapFieldCsv("Noticed", "How Was Interception Made",
            {
                "Interception made as a result of a contact": "contact_noticed",
                "Interception made as a result of staff": "staff_noticed"
            }),
    GroupBooleanCsv("which_contact", "Who was the contact"),
    CopyCsvField("which_contact_other_value", "Other contact", True),

    BooleanCsvField("contact_paid", "Paid the contact", "Paid the contact", ""),
    CopyCsvField("contact_paid_how_much", "Amount Paid to Contact", True),
    CopyCsvField("staff_who_noticed", "Staff who noticed", True),

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

    CopyCsvField("noticed_other_sign_value", "Noticed other sign", True),

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
    FunctionValueExportOnlyCsv("get_how_sure_was_trafficking_display", "How sure that it was a trafficking case"),

    BooleanCsvField("has_signature", "Staff signature on form", "Form is signed", "Form is not signed"),
]

interceptee_data = [
    CopyCsvField("full_name", "{}Name", True),
    MapValueCsvField('gender', "{}Gender", { "Male":"m", "Female":"f"}, export_default="Female"),
    CopyCsvField("age", "{}Age", True),
    DistrictCsvField("district", "{}District"),
    VdcCsvField("vdc", "{}VDC"),
    CopyCsvField("phone_contact", "{}Phone", True),
    CopyCsvField("relation_to", "{}Relationship to...", True),
]

irf_victim_prefix = "Victim "
irf_trafficker_prefix = "Trafficker %d "

def get_irf_export_rows(irfs):
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
            if interceptee.kind == "t":
                continue

            row = []
            # export base IRF
            for field in irf_data:
                row.append(field.exportField(irf))

            # export victim information
            for field in interceptee_data:
                row.append(field.exportField(interceptee))

            # export traffickers
            for trafficker in irf.interceptees.all():
                if trafficker.kind == "v":
                    continue

                for field in interceptee_data:
                    row.append(field.exportField(trafficker))

            rows.append(row)


    return rows

def get_irf_import_rows(csv_map):
    irf_number = csv_map[irf_data[0].title]

    if irf_number is None:
        pass




vif_data = [
    CopyCsvField("vif_number", "VIF Number", False),
    BorderStationExportOnlyCsv("station_name","Station","vif_number"),
    CopyCsvField("date", "Date (on Form)", True),
    DateCsvField("date_time_entered_into_system", "Date Entered"),

    CopyCsvField("number_of_victims", "Number of Victims", True),
    CopyCsvField("number_of_traffickers", "Number of Traffickers", True),

    CopyCsvField("location", "Location", True),
    CopyCsvField("interviewer", "Interviewer", True),

    BooleanCsvField("statement_read_before_beginning", "Statement Read", "Statement was read to the participant", ""),
    BooleanCsvField("permission_to_use_photograph", "Photo Permission", "Permission was given to use photo", ""),

    CopyCsvField("victim_name", "1.1 Name", True),
    CopyCsvField("victim_gender", "1.2 Gender", True),

    DistrictCsvField("victim_address_district", "1.3 District"),
    VdcCsvField("victim_address_vdc", "VDC"),

    CopyCsvField("victim_address_ward", "Ward", True),

    CopyCsvField("victim_phone", "Phone Number", True),
    CopyCsvField("victim_age", "1.4 Age", True),
    CopyCsvField("victim_height", "1.5 Height", True),
    CopyCsvField("victim_weight", "1.6 Weight", True),

    GroupBooleanCsv("victim_caste", "1.7 Caste"),
    CopyCsvField("victim_caste_other_value", "Other Caste", True),

    GroupBooleanCsv("victim_occupation", "1.8 Occupation"),
    CopyCsvField("victim_occupation_other_value", "Other Occupation", True),

    GroupBooleanCsv("victim_marital_status", "1.9 Marital Status"),
    GroupBooleanCsv("victim_lives_with", "1.10 Live With"),
    CopyCsvField("victim_lives_with_other_value", "Live With Other", True),
    CopyCsvField("victim_num_in_family", "1.11 Number of Family Members", True),

    GroupBooleanCsv("victim_primary_guardian", "1.12 Guardian"),
    DistrictCsvField("victim_guardian_address_district", "1.13 Guardian District"),
    VdcCsvField("victim_guardian_address_vdc", "Guardian VDC"),
    CopyCsvField("victim_guardian_address_ward", "Guardian Ward", True),
    CopyCsvField("victim_guardian_phone", "Guardian Phone Number", True),
    GroupBooleanCsv("victim_parents_marital_status", "1.14 Parents' Marital Status"),

    GroupBooleanCsv("victim_education_level", "1.15 Education Level"),
    BooleanCsvField("victim_is_literate", "1.16 Literacy", "Literate", "Illiterate"),

    GroupBooleanCsv("migration_plans", "2.1 Purpose of Going Abroad"),
    CopyCsvField("migration_plans_job_other_value", "Other Job Abroad", True),
    CopyCsvField("migration_plans_other_value", "Other Reason for Going Abroad", True),

    GroupBooleanCsv("primary_motivation", "2.2 Motive for Going Abroad"),
    CopyCsvField("primary_motivation_other_value", "Other Motive", True),
    VictimWhereGoingCsv("victim_where_going", "Destination"),

    BooleanCsvField("manpower_involved","3.1 Involvement of Manpower",
            "Manpower was involved","Manpower was not involved"),
    BooleanCsvField("victim_recruited_in_village", "3.2 Recruited from Village",
            "Was recruited from village", "Was not recruited from village"),
    GroupBooleanCsv("brokers_relation_to_victim", "3.3 Broker's Relation to Victim"),
    CopyCsvField("brokers_relation_to_victim_other_value", "Broker's Relation Other", True),

    FormatCsvFields("victim_married_to_broker_years", "3.4 Duration of Marriage to Broker",
            "Married to Broker for {victim_married_to_broker_years} years and {victim_married_to_broker_months} months",
            "victim_married_to_broker_months"),
    GroupBooleanCsv("victim_how_met_broker", "3.5 Met Broker"),
    CopyCsvField("victim_how_met_broker_other_value", "Met Broker Other", True),
    CopyCsvField("victim_how_met_broker_mobile_explanation", "3.6 Explanation if by mobile", True),

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
    CopyCsvField("victim_primary_means_of_travel_other_value", "Other Means of Travel", True),
    BooleanCsvField("victim_stayed_somewhere_between", "4.3 Transit Stay",
            "Stayed somewhere in transit", "Did not stay anywhere in transit"),
    FormatCsvFields("victim_how_long_stayed_between_days", "4.4 Transit Stay Duration",
              "Stayed for {victim_how_long_stayed_between_days} days starting on {victim_how_long_stayed_between_start_date}",
              "victim_how_long_stayed_between_start_date"),

    BooleanCsvField("victim_was_hidden", "4.5 Transit Hide", "Was kept hidden",""),
    CopyCsvField("victim_was_hidden_explanation", "Transit Hide Explanation", True),
    BooleanCsvField("victim_was_free_to_go_out", "4.6 Transit Free", "Was free to go outside",
            "Was not free to go outside"),
    CopyCsvField("victim_was_free_to_go_out_explanation", "Transit Free Explanation", True),

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
    CopyCsvField("abuse_happened_by_whom", "Person Responsible", True),
    CopyCsvField("abuse_happened_explanation", "Explanation of Abuse", True),

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
    CopyCsvField("how_can_we_serve_you_better", "6.6 How Can We Better Serve You", True),

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
    CopyCsvField("reason_no_legal_interference_value", "Person Interfering with Legal Action", True),
    CopyCsvField("reason_no_legal_other_value", "Other Reason for No Legal Action", True),

    GroupBooleanCsv("interviewer_recommendation", "8.3 Recommendation"),

    BooleanCsvField("other_people_and_places_involved", "8.4 More People or Places Involved in Trafficking",
                "There are other people or places they know of involved in trafficking",
                "There are not any other people or places they know of involved in trafficking"),

    BooleanCsvField("has_signature", "Staff Signature on Form", "Form is signed by staff", "Form is not signed by staff"),

    CopyCsvField("case_notes", "Case Notes", True)
]

person_box_prefix = "PB%d - "

person_box_data = [
    GroupBooleanCsv("who_is_this_relationship", "{}Relationship"),
    GroupBooleanCsv("who_is_this_role", "{}Role"),
    MapValueCsvField("gender", "{}Gender", { "Male":"male", "Female":"female"}),
    CopyCsvField("name", "{}Name", True),
    DistrictCsvField("address_district", "{}District"),
    VdcCsvField("address_vdc", "{}VDC"),
    CopyCsvField("address_ward", "{}Ward", True),
    CopyCsvField("phone", "{}Phone", True),
    CopyCsvField("age", "{}Age", True),
    CopyCsvField("height", "{}Height", True),
    CopyCsvField("weight", "{}Weight", True),
    GroupBooleanCsv("physical_description", "{}Physical Description"),
    CopyCsvField("appearance_other", "{}Appearance", True),
    GroupBooleanCsv("occupation", "{}Occupation"),
    CopyCsvField("occupation_other_value", "{}Other Occupation", True),
    GroupBooleanCsv("political_party", "{}Political Affiliation"),
    CopyCsvField("where_spends_time", "{}How to Locate/Contact", True),
    GroupBooleanCsv("interviewer_believes", "{}Interviewer Believes"),
    GroupBooleanCsv("victim_believes", "{}Victim Believes"),
    FormatCsvFields("associated_with_place_value", "{}Association with Locations",
            "Associated with LB {associated_with_place_value}")
]

location_box_prefix = "LB%d - "

location_box_data = [
    GroupBooleanCsv("which_place", "{}Place"),
    GroupBooleanCsv("what_kind_place", "{}Type of Place"),
    VdcCsvField("vdc", "{}VDC",),
    DistrictCsvField("district", "{}District",),
    CopyCsvField("phone", "{}Phone", True),
    CopyCsvField("signboard", "{}Signboard", True),
    CopyCsvField("location_in_town", "{}Location in Town", True),
    CopyCsvField("color", "{}Color", True),
    CopyCsvField("compound_wall", "{}Compound Wall", True),
    CopyCsvField("number_of_levels", "{}Levels", True),
    CopyCsvField("roof_color", "{}Roof Color", True),
    CopyCsvField("gate_color", "{}Gate Color", True),
    CopyCsvField("person_in_charge", "{}Person in Charge", True),
    CopyCsvField("roof_type", "{}Roof Type", True),
    CopyCsvField("nearby_landmarks", "{}Nearby Landmarks", True),
    CopyCsvField("nearby_signboards", "{}Nearby Signboards", True),
    CopyCsvField("other", "{}Other", True),
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
        for field in person_box_data:
            prefix = person_box_prefix % i
            vif_headers.append(field.title.format(prefix))
        if i < 9:
            for field in location_box_data:
                prefix = location_box_prefix % i
                vif_headers.append(field.title.format(prefix))

    rows.append(vif_headers)


    for vif in vifs:
        row = []

        for field in vif_data:
            row.append(field.exportField(vif))

        pbs = list(vif.person_boxes.all())
        lbs = list(vif.location_boxes.all())

        for idx in range(max(len(pbs), len(lbs))):
            if idx < len(pbs):
                pbs_instance = pbs[idx]
                for field in person_box_data:
                    row.append(field.exportField(pbs_instance))
            else:
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

    print "returning from get_vif_export_rows %d" % len(rows)
    return rows
