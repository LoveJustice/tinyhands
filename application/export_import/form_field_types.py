

def map_value(answer, arguments):
    value = answer
    if 'map' in arguments:
        map_dict = arguments['map']
        if answer in map_dict:
            value = map_dict[answer]
    return value

def export_address(answer, arguments):
    if 'part' in arguments:
        value = parse_part(answer, arguments['part'])
    
    return value

def export_person(answer, arguments):
    if 'part' in arguments:
        value = parse_part(answer, arguments['part'])
    
    return value

answer_type_method = {
    'Address': export_address,
    'Person': export_person
    }

def process_answer(in_answer, arguments):
    if arguments is not None and 'map' in arguments:
        map_dict = arguments['map']
        if in_answer in map_dict:
            out_answer = map_dict[in_answer]
        else:
            out_answer = in_answer
        
        return out_answer

def export_answer_value(object, ie_question):
    
    tmp_answer = object.get_answer(ie_question.question)
    if ie_question.question.answer_type.name in answer_type_method:
        tmp_answer = answer_type_method[ie_question.question.answer_type.name](tmp_answer, ie_question.arguments_json)
        
    if e_question.arguments_json is not None and 'answer_map' in ie_question.arguments_json:
        try:
            answer_map = Answer.objects.get(question=ie_question.question, code=tmp_answer)
            if answer_map.value is not None:
                tmp_answer = answer_map.value
        except ObjectDoesNotExist:
            pass
        
    answer = process_answer(tmp_answer, ie_question.arguments_json)
        
    return answer

def export_field_value(object, ie_field):
    tmp_answer = object.get_field(ie_field.field_name)
    
    if ie_field.export_type in answer_type_method:
        tmp_answer = answer_type_method[ie_field.export_type](tmp_answer, ie_field.arguments_json)
    
    answer = process_answer(tmp_answer, ie_field.arguments_json)
    
    return answer
    
    