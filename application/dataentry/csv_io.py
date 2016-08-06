from parse import parse
from datetime import datetime
from django.db import models
from django.db import transaction
from models import BorderStation
from models import Address1
from models import Address2
from models import Person
from models import Interceptee
from models import InterceptionRecord
from models import VictimInterview
from models import VictimInterviewLocationBox
from models import VictimInterviewPersonBox
from dataentry.google_sheets import GoogleSheetClientThread
from accounts.models import Account
from django.utils.timezone import make_naive, localtime, make_aware
from django.conf import settings

#####################################################
# Note: VIF import logic is not complete in this version
#####################################################

def no_translation(title):
    return title

# export/import field value - no translation
class CopyCsvField:
    def __init__(self, data_name, title, use_none_for_blank, export_null_or_blank_as=""):
        self.data_name = data_name
        self.title = title
        self.use_none_for_blank = use_none_for_blank
        self.export_null_or_blank_as = export_null_or_blank_as

    def importField(self, instance, csv_map, title_prefix = None, name_translation = no_translation):
        errs = []
        if title_prefix is not None:
            column_title = self.title.format(title_prefix )
        else:
            column_title = self.title        
        
        value = csv_map[name_translation(column_title)]
        if value is None and not self.use_none_for_blank:
            value = ""
          
        setattr(instance, self.data_name, value)
            
        return errs

    def exportField(self, instance):
        rv = getattr(instance, self.data_name)
        if rv is None or rv == "":
            rv = self.export_null_or_blank_as

        return rv

# export/import date value
class DateTimeCsvField:
    def __init__(self, data_name, title):
        self.data_name = data_name
        self.title = title

    def importField(self, instance, csv_map, title_prefix = None, name_translation = no_translation):
        errs = []
        if title_prefix is not None:
            column_title = self.title.format(title_prefix)
        else:
            column_title = self.title

        value = csv_map[name_translation(column_title)]
        if value is not None:
            try:
                parsed_value = datetime.strptime(value, "%m/%d/%Y %H:%M:%S")
                parsed_value = make_aware(parsed_value)
            except:
                try:
                    parsed_value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                    parsed_value = make_aware(parsed_value)
                except:
                    errs.append(column_title)
                
            setattr(instance, self.data_name, parsed_value)
        else:
            errs.append(column_title)
        
        return errs

    def exportField(self, instance):
        value = getattr(instance, self.data_name)
        local_val = localtime(value)
        local_val = local_val.replace(microsecond=0)
        return make_naive(local_val, local_val.tzinfo)
    
class DateCsvField:
    def __init__(self, data_name, title):
        self.data_name = data_name
        self.title = title

    def importField(self, instance, csv_map, title_prefix = None, name_translation = no_translation):
        errs = []
        if title_prefix is not None:
            column_title = self.title.format(title_prefix)
        else:
            column_title = self.title

        value = csv_map[name_translation(column_title)]
        if value is not None:
            try:
                parsed_value = datetime.strptime(value, "%m/%d/%Y")
                parsed_value = make_aware(parsed_value)
                setattr(instance, self.data_name, parsed_value)
            except:
                errs.append(column_title)
        else:
            errs.append(column_title)
        
        return errs

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

    def importField(self, instance, csv_map, title_prefix = None, name_translation = no_translation):
        errs = []
        if title_prefix is not None:
            column_title = self.title.format(title_prefix)
        else:
            column_title = self.title
       
        value = csv_map[name_translation(column_title)]
        
        if value is None:
            value = ""
        
        if value == self.true_string:
            value = True
        elif value == self.false_string:
            value = False
        elif value == "":
            value = None
        else:
            errs.append(column_title)
            return errs

        setattr(instance, self.data_name, value)
        
        return errs

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
    def __init__(self, data_name, title, allow_none = True):
        self.data_name = data_name
        self.title = title
        self.allow_none = allow_none

    def importField(self, instance, csv_map, title_prefix = None, name_translation = no_translation):
        errs = []
        if title_prefix is not None:
            column_title = self.title.format(title_prefix)
        else:
            column_title = self.title
        
        value = csv_map[name_translation(column_title)]
        if value is not None:
            for field in instance._meta.fields:
                if field.name.startswith(self.data_name) and (
                        isinstance(field, models.BooleanField) or isinstance(field, models.NullBooleanField)):
                    if field.verbose_name == value:
                        setattr(instance, field.name, True)
                        return

            errs.append(column_title)
        else:
            if not self.allow_none:
                errs.append(column_title)
            
        return errs

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

    def importField(self, instance, csv_map, title_prefix = None, name_translation = no_translation):
        errs = []
        if title_prefix is not None:
            column_title = self.title.format(title_prefix)
        else:
            column_title = self.title
        
        value = csv_map[name_translation(column_title)]
        if value is None or value == '':
            setattr(instance, self.data_name, False)
            setattr(instance, self.value_name, '')
        else:
            setattr(instance, self.data_name, True)
            setattr(instance, self.value_name, value)
            
        return errs

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

    def importField(self, instance, csv_map, title_prefix = None, name_translation = no_translation):
        errs = []
        if title_prefix is not None:
            column_title = self.title.format(title_prefix)
        else:
            column_title = self.title
        
        value = csv_map[name_translation(column_title)]
        if value is not None:
            field_name = self.value_to_field_map[value]
            if field_name is not None:
                setattr(instance, field_name, True)
            else:
                errs.append(column_title)
            
        return errs

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

    def importField(self, instance, csv_map, title_prefix = None, name_translation = no_translation):
        errs = []
        if title_prefix is not None:
            column_title = self.title.format(title_prefix)
        else:
            column_title = self.title
        
        tmp = csv_map[name_translation(column_title)]
        if tmp is None or tmp == "":
            return errs
       
        parse_map = parse(self.formatString, tmp)
        if len(parse_map.named) != len(self.additional) +1:
            errs.append(column_title + ':Unexpected number of values parsed from "' +
                    tmp + '"');
            return errs

        tmp_val = parse_map.named[self.data_name]
        if tmp_val is None:
            errs.append(column_title + ':Unable to parse data field value from "' + tmp + '"')
            return errs

        setattr(instance, self.data_name, tmp_val)

        for add_name in self.additional:
            tmp_val = parse_map[add_name]
            if tmp_val is None:
                errs.append(column_title + ':Unable to parse value for additional field ' +
                        add_name + ' from value="' + tmp +'"')
            setattr(instance, add_name, tmp_val)
            
        return errs


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

# Export/import Address1 field
class Address1CsvField:
    def __init__(self, data_name, title):
        self.data_name = data_name
        self.title = title

    def importField(self, instance, csv_map, title_prefix = None, name_translation = no_translation):
        errs = []
        if title_prefix is not None:
            column_title = self.title.format(title_prefix)
        else:
            column_title = self.title
        
        value = csv_map[name_translation(column_title)]
        if value is not None and value != "":
            try:
                address1 = Address1.objects.get(name=value)
            except:
                address1 = None
                errs.append(column_title + ':Unable to locate address 1 with value="' + value + '"')
        else:
            address1 = None
        
        setattr(instance, self.data_name, address1)
            
            
        return errs


    def exportField(self, instance):
        value = ""
        try:
            tmp = getattr(instance, self.data_name)
            if tmp is not None:
                value = tmp
        finally:
            return value

# Export/import Address2 field
class Address2CsvField:
    def __init__(self, data_name, title, address1_data_name):
        self.data_name = data_name
        self.title = title
        self.address1_data_name = address1_data_name

    def importField(self, instance, csv_map, title_prefix = None, name_translation = no_translation):
        errs = []
        address1 = getattr(instance, self.address1_data_name)
        if title_prefix is not None:
            column_title = self.title.format(title_prefix)
        else:
            column_title = self.title
        
        value = csv_map[name_translation(column_title)]
        if value is not None and value != "":
            if address1 is None:
                address2 = None
                errs.append(column_title + ':Value="' + value + '", but address1 is not populated')
            else:
                try:
                    address2 = Address2.objects.get(name=value, address1=address1)
                except:
                    errs.append(column_title + ':Unable to locate address 2 with value="' + value +
                                '" in "' + address1.name + '"')
                    address2 = None
        else:
            address2 = None
            
        
        setattr(instance, self.data_name, address2)
            
        return errs


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
    def __init__(self, data_name, title, value_map, export_default="", required_nonempty=False):
        self.data_name = data_name
        self.title = title
        self.value_map = value_map
        self.export_default = export_default
        self.required_nonempty = required_nonempty

    def importField(self, instance, csv_map, title_prefix = None, name_translation = no_translation):
        errs = []
        if title_prefix is not None:
            column_title = self.title.format(title_prefix)
        else:
            column_title = self.title
        
        value = csv_map[name_translation(column_title)]
        if value is not None:
            mapped_value = self.value_map[value]
            if mapped_value is not None:
                setattr(instance, self.data_name, mapped_value)
            else:
                errs.append(column_title)
        else:
            if self.required_nonempty:
                errs.append(column_title)
            else:
                setattr(instance, self.data_name, value)
            
        return errs

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

    def importField(self, instance, csv_map, title_prefix = None, name_translation = no_translation):
        errs = []
        return errs

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

    def importField(self, instance, csv_map, title_prefix = None, name_translation = no_translation):
        errs = []
        return errs

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

    def importField(self, instance, csv_map, title_prefix = None, name_translation = no_translation):
        errs = []
        if title_prefix is not None:
            column_title = self.title.format(title_prefix)
        else:
            column_title = self.title
        
        value = csv_map[name_translation(column_title)]
        if value is not None:
            found = False
            for msg in self.msgs.keys():
                fmt = self.msgs[msg]
                rv = parse(fmt, value)
                if rv is not None:
                    found = True
                    setattr(instance, msg, True)
                    if len(rv.fixed) > 0:
                        if (rv.fixed[0] == 'None'):
                            break
                        else:
                            instance.victim_how_expense_was_paid_amount = rv.fixed[0]
                            break
            if not found:
                # if the amount was blank in the export, the parse will fail.
                # check to see if the format matches with the empty string where the amount would be
                for msg in self.msgs.keys():
                    fmt = self.msgs[msg];
                    fmt = fmt.replace("{}","");
                    if value == fmt:
                        setattr(instance, msg, True)
                        break
                        
            
        return errs

    def exportField(self, instance):
        for msg in self.msgs.keys():
            bool_val = getattr(instance, msg)
            if bool_val is not None:
                if bool_val:
                    fmt = self.msgs[msg]
                    amt = instance.victim_how_expense_was_paid_amount
                    if amt is None:
                        amt = ""

                    return fmt.format(amt)

        return ""

class BrokerPromisesCsv(FormatCsvFields):
    def __init__(self, data_name, title, formatString):
        FormatCsvFields.__init__(self, data_name, title, formatString)
        
    def importField(self, instance, csv_map, title_prefix = None, name_translation = no_translation):
        errs = []
        if title_prefix is not None:
            column_title = self.title.format(title_prefix)
        else:
            column_title = self.title
        
        value = csv_map[name_translation(column_title)]
        if value is not None and value != "":
            FormatCsvFields.importField(self, instance, csv_map, title_prefix = title_prefix, name_translation = name_translation)
        return errs

    def exportField(self, instance):
        tmp = getattr(instance, self.data_name)
        if tmp is None or tmp == 0:
            return ""

        return FormatCsvFields.exportField(self, instance)

class VictimWhereGoingCsv:
    india_prefix = "victim_where_going_india"
    gulf_prefix = "victim_where_going_gulf"  
    just_india = "India"
    just_gulf = "Gulf / Other"    
    unknown_in_india = "Unknown location in India"
    unknown_in_gulf = "Unknown location in Gulf / Other"
    
    india_other_suffix = ", India"
    
    def __init__(self, data_name, title):
        self.data_name = data_name
        self.title = title

    def importField(self, instance, csv_map, title_prefix = None, name_translation = no_translation):
        errs = []
        if title_prefix is not None:
            column_title = self.title.format(title_prefix)
        else:
            column_title = self.title
        
        found = False
        value = csv_map[name_translation(column_title)]
        for field in instance._meta.fields:
            if field.verbose_name == value:
                if field.name.startswith(VictimWhereGoingCsv.india_prefix):
                    instance.victim_where_going_region_india = True
                    setattr(instance, field.name, True)
                    found = True
                    break
                elif field.name.startswith(VictimWhereGoingCsv.gulf_prefix) : 
                    instance.victim_where_going_region_gulf = True
                    setattr(instance, field.name, True)
                    found = True
                    break
        
        if found == False:
            if value is None:
                pass
            elif value == VictimWhereGoingCsv.unknown_in_india:
                instance.victim_where_going_india_didnt_know = True
                instance.victim_where_going_region_india = True
            elif value == VictimWhereGoingCsv.just_india:
                instance.victim_where_going_region_india = True
            elif value.endswith(VictimWhereGoingCsv.india_other_suffix):
                instance.victim_where_going_region_india = True
                instance.victim_where_going_india_other = True
                instance.victim_where_going_india_other_value = value[:-len(VictimWhereGoingCsv.india_other_suffix)]
            elif value == VictimWhereGoingCsv.unknown_in_gulf:
                instance.victim_where_going_region_gulf = True
                instance.victim_where_going_gulf_didnt_know = True
            elif value == VictimWhereGoingCsv.just_gulf:
                instance.victim_where_going_region_gulf = True
            elif value != "":
                # Didn't match any other value - so we have to assume
                # it is gulf other
                instance.victim_where_going_region_gulf = True
                instance.victim_where_going_gulf_other = True
                instance.victim_where_going_gulf_other_value = value
             
        return errs

    def exportField(self, instance):
        if instance.victim_where_going_region_india:
            if instance.victim_where_going_india_didnt_know:
                return VictimWhereGoingCsv.unknown_in_india
            elif instance.victim_where_going_india_other:
                other_value = instance.victim_where_going_india_other_value
                if other_value is None or other_value == "":
                    return VictimWhereGoingCsv.just_india
                else:
                    return other_value + VictimWhereGoingCsv.india_other_suffix
            else:
                val = self.verbose_name(instance, VictimWhereGoingCsv.india_prefix, None)
                if val is None:
                    return VictimWhereGoingCsv.just_india
                else:
                    return val

        elif instance.victim_where_going_region_gulf:
            if instance.victim_where_going_gulf_didnt_know:
                return VictimWhereGoingCsv.unknown_in_gulf
            elif instance.victim_where_going_gulf_other:
                other_value = instance.victim_where_going_gulf_other_value
                if other_value is None or other_value == "":
                    return VictimWhereGoingCsv.just_gulf
                else:
                    return other_value
            else:
                val = self.verbose_name(instance, VictimWhereGoingCsv.gulf_prefix, None)
                if val is None:
                    return VictimWhereGoingCsv.just_gulf
                else:
                    return val
        else:
            return ""

    def verbose_name(self, instance, prefix, default):
        for field in instance._meta.fields:
            if field.name.startswith(prefix):
                value = getattr(instance, field.name)
                if value:
                    if isinstance(field, models.BooleanField) or isinstance(field, models.NullBooleanField):
                        return field.verbose_name
        return default
    
    

class LegalActionCsv:
    no_action = "No legal action has been taken"
    fir_action = "An FIR has been filed"
    doe_action = "A DoFE complaint has been filed"
    both_action = "An FIR and a DoFE complaint have both been filed"
    
    
    def __init__(self, data_name, title):
        self.data_name = data_name
        self.title = title

    def importField(self, instance, csv_map, title_prefix = None, name_translation = no_translation):
        errs = []
        if title_prefix is not None:
            column_title = self.title.format(title_prefix)
        else:
            column_title = self.title
        
        value = csv_map[name_translation(column_title)]
        if value is None:
            errs.append(column_title +":Value not found")
            return errs
        if value == LegalActionCsv.no_action:
            instance.legal_action_against_traffickers_no = True
        elif value == LegalActionCsv.both_action:
            instance.legal_action_against_traffickers_fir_filed = True
            instance.legal_action_against_traffickers_dofe_complaint = True
        elif value == LegalActionCsv.fir_action:
            instance.legal_action_against_traffickers_fir_filed = True
        elif value == LegalActionCsv.doe_action:
            instance.legal_action_against_traffickers_dofe_complaint = True
            
        return errs

    def exportField(self, instance):
        if instance.legal_action_against_traffickers_no:
            return LegalActionCsv.no_action
        if instance.legal_action_against_traffickers_fir_filed and instance.legal_action_against_traffickers_dofe_complaint:
            return LegalActionCsv.both_action
        if instance.legal_action_against_traffickers_fir_filed:
            return LegalActionCsv.fir_action
        if instance.legal_action_against_traffickers_dofe_complaint:
            return LegalActionCsv.doe_action

class FirDofeCsv:
    def __init__(self, data_name, title):
        self.data_name = data_name
        self.title = title
        self.separator = ", "

    def importField(self, instance, csv_map, title_prefix = None, name_translation = no_translation):
        errs = []
        if title_prefix is not None:
            column_title = self.title.format(title_prefix)
        else:
            column_title = self.title
        
        value = csv_map[name_translation(column_title)]
        if value is None:
            errs.append(column_title + ":Value not found")
            return

        if value != "":
            parts = value.partition(self.separator)
            if parts[2] != "":
                instance.legal_action_fir_against_value = parts[0]
                instance.legal_action_dofe_against_value = parts[2]
            elif instance.legal_action_against_traffickers_fir_filed:
                instance.legal_action_fir_against_value = value
            elif instance.legal_action_against_traffickers_dofe_complaint:
                instance.legal_action_dofe_against_value = value
            else:
                errs.append(column_title + 'Value="' + value + '" provided, but both legal action flags are false')
            
        return errs


    def exportField(self, instance):
        value = ""
        if instance.legal_action_fir_against_value != "" and instance.legal_action_dofe_against_value != "":
            value += instance.legal_action_fir_against_value + self.separator + instance.legal_action_dofe_against_value
        elif instance.legal_action_fir_against_value != "":
            value += instance.legal_action_fir_against_value
        elif instance.legal_action_dofe_against_value != "":
            value += instance.legal_action_dofe_against_value
        return value

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
                "Interception made as a result of staff": "staff_noticed"
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

    BooleanCsvField("has_signature", "Staff signature on form", "Form is signed", "Form is not signed"),
]

additional_irf_import_data = [
    DateCsvField("date_form_received", "Date Received"),
]


victim_data = [
    "1.1 Name",
    "1.2 Gender",
    "1.3 Address1",
    "Address2",
    "Phone Number",
    "1.4 Age",
]

person_box_person_data = [
    MapValueCsvField("gender", "{}Gender", { "Male":"M", "Female":"F"}, required_nonempty=True),
    CopyCsvField("full_name", "{}Name", True),
    Address1CsvField("address1", "{}Address1"),
    Address2CsvField("address2", "{}Address2", "address1"),
    CopyCsvField("phone_contact", "{}Phone", False),
    CopyCsvField("age", "{}Age", True),
]

interceptee_person_data = [
    CopyCsvField("full_name", "{}Name", True),
    MapValueCsvField('gender', "{}Gender", { "Male":"M", "Female":"F"}, export_default="Female", required_nonempty=True),
    CopyCsvField("age", "{}Age", True),
    Address1CsvField("address1", "{}Address1"),
    Address2CsvField("address2", "{}Address2", "address1"),
    CopyCsvField("phone_contact", "{}Phone", False),
]

interceptee_data = []
interceptee_data.extend(interceptee_person_data)
interceptee_data.extend([CopyCsvField("relation_to", "{}Relationship to...", False)])

interceptee_import_data = [
    CopyCsvField("kind", "{}Kind", True),
]
interceptee_import_data.extend(interceptee_data)

irf_victim_prefix = "Victim "
irf_trafficker_prefix = "Trafficker %d "
irf_interceptee_prefix = "Interceptee %d "

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


def import_irf_row(irfDict):
    errList = []
    
    entered_by = Account.objects.get(email=settings.IMPORT_ACCOUNT_EMAIL)
    
    
    person_titles = []
    for field in interceptee_person_data:
        person_titles.append(field.title)
    
    
    irf_nbr = irfDict[GoogleSheetClientThread.spreadsheet_header_from_export_header(irf_data[0].title)]
    if irf_nbr is None:
        errList.append("Unable to find data for IRF Number")
        return errList
    else:
        try:
            InterceptionRecord.objects.get(irf_number=irf_nbr)
            errList.append("IRF already exists")
            return errList
        except:
            pass
    
    irf = InterceptionRecord()
    for field in irf_data:
        try:
            errs = field.importField(irf, irfDict, name_translation = GoogleSheetClientThread.spreadsheet_header_from_export_header)
            if errs is not None:
                errList.extend(errs)
        except:
            errList.append(field.title + ":Unexpected error - contact developer")

            
    for field in additional_irf_import_data:
        try:
            errs = field.importField(irf, irfDict, name_translation = GoogleSheetClientThread.spreadsheet_header_from_export_header)
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
        kind_title = GoogleSheetClientThread.spreadsheet_header_from_export_header(kind_title)                                                                                  
        if irfDict[kind_title] is None:
            continue

        interceptee = Interceptee()
        person = Person()
        for field in interceptee_import_data:
            try:
                if field.title in person_titles:
                    errs = field.importField(person, irfDict, prefix, 
                            name_translation = GoogleSheetClientThread.spreadsheet_header_from_export_header)
                else:
                    errs = field.importField(interceptee, irfDict, prefix, 
                            name_translation = GoogleSheetClientThread.spreadsheet_header_from_export_header)          
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
            errList.append("Unexpected error saving IRF in database")
                
        GoogleSheetClientThread.update_irf(irf_nbr)        
        
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
    MapValueCsvField("gender", "1.2 Gender", { "male":"M", "female":"F"}, export_default="female", required_nonempty=True),

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
    
    vif_nbr = vifDict[GoogleSheetClientThread.spreadsheet_header_from_export_header(vif_data[0].title)]
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
                        name_translation = GoogleSheetClientThread.spreadsheet_header_from_export_header)
            else:
                errs = field.importField(vif, vifDict, "", 
                        name_translation = GoogleSheetClientThread.spreadsheet_header_from_export_header)
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
            tmp = vifDict.get(GoogleSheetClientThread.spreadsheet_header_from_export_header(field.title.format(prefix)))
            if tmp is not None:
                found = True
                break
        if found:
            tmp_person = Person()
            for field in person_box_person_data:
                try:
                    errs = field.importField(tmp_person, vifDict, prefix, 
                            name_translation = GoogleSheetClientThread.spreadsheet_header_from_export_header)
                    if errs is not None:
                        errList.extend(errs)     
                except:
                    errList.append(field.title.format(prefix) + ":Unexpected error - contact developer")
            
            person_box_persons.append(tmp_person)
               
            tmp_person_box = VictimInterviewPersonBox()
            for field in person_box_data:
                try:
                    errs = field.importField(tmp_person_box, vifDict, prefix, 
                            name_translation = GoogleSheetClientThread.spreadsheet_header_from_export_header)
                    if errs is not None:
                        errList.extend(errs)
                except:
                    errList.append(field.title.format(prefix) + ":Unexpected error - contact developer")
                
            person_boxes.append(tmp_person_box)

        prefix = location_box_prefix % idx
        found = False
        for field in location_box_data:
            tmp = vifDict.get(GoogleSheetClientThread.spreadsheet_header_from_export_header(field.title.format(prefix)))
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
                                name_translation = GoogleSheetClientThread.spreadsheet_header_from_export_header)
                        if errs is not None:
                            errList.extend(errs)
                    except:
                        errList.append(field.title.format(prefix) + ":Unexpected error - contact developer")
                    
            for field in location_box_data:
                if not isinstance(field, Address1CsvField):
                    try:
                        errs = field.importField(tmp_location, vifDict, prefix, 
                                name_translation = GoogleSheetClientThread.spreadsheet_header_from_export_header)
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
        except:
            errList.append("Unexpected error saving VIF in database - contact developer")
                          
        GoogleSheetClientThread.update_vif(vif_nbr)        
        
    return errList
