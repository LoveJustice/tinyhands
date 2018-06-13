

def map_value(answer, arguments):
    value = answer
    if 'map' in arguments:
        map_dict = arguments['map']
        if answer in map_dict:
            value = map_dict[answer]
    return value
        
def export_string(answer, arguments):
    value = map_value(answer, arguments)
    return value

def export_integer(answer, arguments):
    pass

def export_float(answer, arguments):
    pass

def export_radio(answer, arguments):
    pass

def export_dropdown(answer, arguments):
    pass

def export_checkbox(answer, arguments):
    pass

def export_address(answer, arguments):
    pass

def export_phone(answer, arguments):
    return answer

def export_date(answer, arguments):
    return str(answer)

def export_datetime(answer, arguments):
    local_val = localtime(answer)
    local_val = local_val.replace(microsecond=0)
    return make_naive(local_val, local_val.tzinfo)

def export_person(answer, arguments):
    pass

def get_export_value(object, ie_question):
    answer_type_method = {
        'String': export_string,
        'Integer': export_integer,
        'Float': export_float,
        'RadioButton': export_radio,
        'Dropdown': export_dropdown,
        'Checkbox': export_checkbox,
        'Address': export_address,
        'Phone': export_phone,
        'Date': export_date,
        'DateTime': export_datetime,
        'Person': export_person
        }
    
    answer = object.get_answer(ie_question.question)
    if ie_question.arguments_json is not None:
        mapping = question.arguments_json['mapping']
    