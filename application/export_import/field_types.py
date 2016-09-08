from parse import parse
from datetime import datetime
from django.db import models
from dataentry.models import BorderStation
from dataentry.models import Address1
from dataentry.models import Address2
from django.utils.timezone import make_naive, localtime, make_aware

def no_translation(title):
    return title

# export/import field value - no translation
class CopyCsvField:
    def __init__(self, data_name, title, use_none_for_blank, export_null_or_blank_as="", allow_null_or_blank_import = True):
        self.data_name = data_name
        self.title = title
        self.use_none_for_blank = use_none_for_blank
        self.export_null_or_blank_as = export_null_or_blank_as
        self.allow_null_or_blank_import = allow_null_or_blank_import

    def importField(self, instance, csv_map, title_prefix = None, name_translation = no_translation):
        errs = []
        if title_prefix is not None:
            column_title = self.title.format(title_prefix )
        else:
            column_title = self.title        
        
        value = csv_map[name_translation(column_title)]
        if value is None:
            if not self.allow_null_or_blank_import:
                errs.append(column_title)
            elif not self.use_none_for_blank:
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
    parse_options = ["%m/%d/%Y %H:%M:%S","%Y-%m-%d %H:%M:%S","%m/%d/%Y %I:%M:%S %p","%Y-%m-%d %I:%M:%S %p",
                     "%m/%d/%y %H:%M:%S","%m/%d/%y %I:%M:%S %p",
                     "%m/%d/%Y %H:%M","%Y-%m-%d %H:%M","%m/%d/%Y %I:%M %p","%Y-%m-%d %I:%M %p",
                     "%m/%d/%y %H:%M","%m/%d/%y %I:%M %p"];
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
            parsed_value = None
            for fmt in DateTimeCsvField.parse_options:
                try:
                    parsed_value = datetime.strptime(value, fmt)
                    parsed_value = make_aware(parsed_value)
                    setattr(instance, self.data_name, parsed_value)
                    break
                except:
                    #print "Failed to parse datetime value=" + value + " with format " + fmt
                    pass
                
            if parsed_value is None:
                errs.append(column_title)
        else:
            errs.append(column_title)
        
        return errs

    def exportField(self, instance):
        value = getattr(instance, self.data_name)
        local_val = localtime(value)
        local_val = local_val.replace(microsecond=0)
        return make_naive(local_val, local_val.tzinfo)
    
class DateCsvField:
    parse_options = ["%m/%d/%Y","%Y-%m-%d", "%m/%d/%y"];
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
            parsed_value = None
            for fmt in DateCsvField.parse_options:
                try:
                    parsed_value = datetime.strptime(value, fmt)
                    parsed_value = make_aware(parsed_value)
                    setattr(instance, self.data_name, parsed_value)
                except:
                    pass
                
            if parsed_value is None:
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
    def __init__(self, data_name, title, true_string, false_string, depend_name = None, allow_null_or_blank_import = True):
        self.data_name = data_name
        self.title = title
        self.true_string = true_string
        self.false_string = false_string
        self.depend_name = depend_name
        self.allow_null_or_blank_import = allow_null_or_blank_import

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
        elif self.allow_null_or_blank_import:
            if value == "":
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
    set_no_field = "SET_NO_FIELD"
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
                if field_name != MapFieldCsv.set_no_field:
                    setattr(instance, field_name, True)
            else:
                errs.append(column_title)
            
        return errs

    def exportField(self, instance):
        for key, val in self.value_to_field_map.items():
            if val != MapFieldCsv.set_no_field:
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
            try:
                mapped_value = self.value_map[value]
                if mapped_value is not None:
                    setattr(instance, self.data_name, mapped_value)
                else:
                    errs.append(column_title)
            except:
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

