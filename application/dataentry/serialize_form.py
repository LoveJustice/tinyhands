

class SerializeForm:
    @staticmethod
    def person_serialize(question, field_value=None, response_value=None):
        if field_value is not None:
            person = field_value
        elif response_value is not None:
            try:
                person = Person.objects.get(id=int(response_value))
            except:
                #log
                person = None
        else:
            person = None
        
        if person is not None:
            data = {}
            data['name'] = { 'value': person.full_name }
            if person.address2 is not None:
                data['address1'] = {
                        'id': person.address2.address1.id,
                        'value': person.address2.address1.name
                    }
                data['address2'] = {
                        'id': person.address2.id,
                        'value': person.address2.name
                    }
            if person.phone_contact is not None:
                data['phone'] = {'value': person.phone_contact }
                
            if person.gender == 'M':
                data['gender'] = 'Male'
            elif person.gender == 'F':
                data['gender'] = 'Female'
            else:
                data['gender'] = 'Unknown'
            
            if person.age is not None:
                data['age'] = person.age
            
            return data
        else:
            return None
    
    @staticmethod   
    def address_serialize(question, field_value=None, response_value=None):
        if field_value is not None:
           address2 = field_value
        elif response_value is not None:
            try:
                address2 = Address2.objects.get(id=int(response_value))
            except:
                # log
                address2 = None
        else:
            address2 = None
        
        if address2 is not None:
            addr1 = {}
            addr1['id'] = address2.address1.id
            addr1['value'] = address2.address1.name
            
            addr2 = {}
            addr2['id'] = address2.id
            addr2['value'] = address2.name
            
            return {'address1':addr1, 'address2': addr2}
        else:
            return None
            
            
    
    @staticmethod   
    def radiobutton_serialize(question, field_value=None, response_value=None):
        data = {}
        
        if field_value is not None:
            code = field_value
        elif response_value is not None:
            code = rsponse_value
        else:
            code = None
        
        if code is not None:
            try:
                answer = Answer.object.get(question=question, code=code)
                val = { "value": answer.value }
            except:
                val = { "value": code }
        else:
            val = None
        
        return val
    
    @staticmethod   
    def dropdown_serialize(question, field_value=None, response_value=None):
        data = {}
        
        if field_value is not None:
            code = field_value
        elif response_value is not None:
            code = rsponse_value
        else:
            code =  None
        
        if code is not None:
            try:
                answer = Answer.object.get(question=question, code=code)
                val = { "value": answer.value }
            except:
                val = { "value": code }
        else:
            val = None
        
        return val
    
    @staticmethod
    def checkbox_serialize(question, field_value=None, response_value=None):
        if field_value is not None:
            if isinstance(field_value, bool):
                if field_value == True:
                    val = 'True'
                elif field_value == False:
                    val = 'False'
            else:
                val = field_value
        elif response_value is not None:
            val = rsponse_value
        else:
            val = None
        
        if val is not None:
            return {'value': val }
        else:
            return None  
            
    question_serialization_method = {
        'Person': SerializeForm.person_serialize,
        'Address': SerializeForm.address_serialize,
        'RadioButton': SerializeForm.radiobutton_serialize,
        'Dropdown': SerializeForm.dropdown_serialize
    }
                
    def serializeResponses(self, question_layouts, object, response_model):
        question_list = []
        for question_layout in question_layouts:
            question = question_layout.question
            question_data = { 'question_id': question.id }
            try:
                the_storage = QuestionStorage.objects.get(question = question)
                
                # response is stored  as a field in the form object
                question_data['storage_id'] = object.id
                tmp_val = getattr(object, the_storage.field_name, None)
                if tmp is not None:
                    if question.answer_type.name in question_serialization_method:
                        val = question_serialization_method(question, field_value=tmp)
                    else:
                        val = { "value": tmp }
                else:
                    val = None
            except:
                if response_model is not None:
                    try:
                        # response for question is stored in the response table
                        response = response_model.objects.get(form=object, question=question)
                        question_data['storage_id'] = response.id
                        if question.answer_type.name in question_serialization_method:
                            val = question_serialization_method(question, response_value=response.value)
                        else:
                            val = { "value": response.value }
                    except:
                        # no response for question
                        val = None
                else:
                    # log configuration error - question should either have storage defined or the response_model should not be None
                    val = None
            
            if val is not None:
                question_data['response']  = val
                question_list.append(question_data)
                
        return question_list
    
    # Serialize category that is not of type card
    def serializeCategory(self, object, response_model, category):
        question_layouts = Question.objects.filter(category=category)
        return self.serializeResponses(question_layouts, object, response_model)
    
    # Serialize all cards for a given category
    def serialize_cards(form, category):
        card_storage = CardStorage(category = category)
        storage = card_storage.storage
        mod = __import__(storage.module_name, fromlist=[storage.form_model_name, storage.response_model_name])
        card_class = getattr(mod, storage.form_model_name)
        card_response_class = getattr(mod, storage.response_model_name)
        question_layouts = QuestionLayout.objects.filter(category=category)
        
        card_data = {
            'category_id': category.id
        }
        instance_list = []
        
        cards = card_class.objects.filter(form=form)
        for card in cards:
            data = {"storage_id": card.id}
            data['questions'] = self.serializeResponses(question_layouts, card, card_rsponse_class)
            instance_list.append(data)
        
        card_data['instances'] = instance_list
        return card_data

    
    def serialize(self, object, station, form_type):
        today = date.today()
        form = Form.objects.get(form_type=form_type, country=object.station.operating_country, start_date__lte=today, end_date__gte=today)
        storarge = Storage.objects.get(form_model_name = object.__class__.__name__)
        if storage.response_model_name is not None:
            mod = __import__(storage.module_name, fromlist=[storage.response_model_name])
            response_model = getattr(mod, storage.response_model_name, None)
        else:
            response_model = None
            
        form_dict = {}
        form_dict['form_id'] = form.id
        form_dict['station_id'] = station.id
        form_dict['station_code'] = station.code
        form_dict['station_name'] = station.name
        form_dict['country_id'] = station.operating_country.id
        
        if object is not None:
            form_dict['storage_id'] = object.id
            
            categories = Categories.objects.filter(form = form)
            response_list = []
            card_list = []
            for category in categories:
                if category.category_type.name == 'card':
                    try:
                        card_list = card_list + self.serialize_cards(object, category)
                    except:
                        # log failure
                        pass
                else:
                    try:
                        response_list = response_list + self.serializeCategory(object, response_model, category)
                    except:
                        #log error
                        pass
                    
            form_dict['responses'] = response_list
            form_dict['cards'] = card_list
       
        return form_dict
    
    @staticmethod
    def person_deserialize(response, question, return_as_string, allow_update):
        storage_id = get(response, 'storage_id')
        name = response.get('name')
        phone = response.get('phone')
        gender = response.get('gender')
        if gender == 'Female':
            gender_code = 'F'
        elif gender == 'Male':
            gender_code = 'M'
        else:
            gender_code = 'U'
        age = response.get('age')
        
        address1_dict = response.get('address1')
        address2_dict = response.get('address2')
        
        if address1_dict is not None and address2_dict is not None:
            address1_id = address1_dict.get(id)
            if address1_id is None:
                address_name = address1_dict.get('name')
                try:
                    # check for an existing address1 with the same name
                    address1 = Address1.objects.get(name=address_name)
                except:
                    address1 = Address1()
                    address1.name = address_name
                    address1.save()
            else:
                address1 = Address1.objects.get(id=address1_id)
            
            address2_id = address2_dict.get('id')
            if address2_id is None:
                address_name = address2_dict.get('name')
                try:
                    address2 = Address2.get(address1=address1, name=address_name)
                except:
                    address2 = Address2()
                    address2.address1 = address1
                    address2.name = address_name
                    address2.save()
            else:
                address2 = Address2.get(id = address2_id)
        
        
        if storage_id is None:
            person = Person()
            person.address1 = address1
            person.address2 = address2
            person.name = name
            person.phone = phone
            person.gender = gender_code
            person.age = age
            person.save()
        else:
            person = Person.objects.get(id=storage_id)
            if not allow_update and (
                    person.address1 != address1 or
                    person.address2 != address2 or
                    person.name != name or
                    person.phone != phone or
                    person.gender != gender_code or
                    person.age != age):
                person = Person()
                
            person.address1 = address1
            person.address2 = address2
            person.name = name
            person.phone = phone
            person.gender = gender_code
            person.age = age
            person.save()
            
        return person  
    
    @staticmethod
    def address_deserialize(response, question, return_as_string, mode):
        address1_dict = response.get('address1')
        address2_dict = response.get('address2')
        
        if address1_dict is not None and address2_dict is not None:
            address1_id = address1_dict.get(id)
            if address1_id is None:
                address_name = address1_dict.get('name')
                try:
                    # check for an existing address1 with the same name
                    address1 = Address1.objects.get(name=address_name)
                except:
                    address1 = Address1()
                    address1.name = address_name
                    address1.save()
            else:
                address1 = Address1.objects.get(id=address1_id)
            
            address2_id = address2_dict.get('id')
            if address2_id is None:
                address_name = address2_dict.get('name')
                try:
                    address2 = Address2.get(address1=address1, name=address_name)
                except:
                    address2 = Address2()
                    address2.address1 = address1
                    address2.name = address_name
                    address2.save()
            else:
                address2 = Address2.get(id = address2_id)
        else:
            address2 = None
        
        return address2        
    
    @staticmethod
    def radiobutton_deserialize(response, question, return_as_string, mode):
        value = response.get('value')
        try:
            answer = Answer.objects.get(question=question, value=value)
            if answer.code is not None:
                value = answer.code
        except:
            # answer for translating to code (could be other)
            pass
        
        return value
        
        
    
    @staticmethod   
    def dropdown_deserialize(response, question, return_as_string, mode):
        value = response.get('value')
        try:
            answer = Answer.objects.get(question=question, value=value)
            if answer.code is not None:
                value = answer.code
        except:
            # No coded value for mapping the result
            pass
        
        return value
    
    @staticmethod
    def checkbox_deserialize(response, question, return_as_string, mode):
        value = response.get('value')
        if not (return_as_string or 'textBox' in question.params):
            if value == 'True':
                value = True
            elif value == 'False':
                value = False
            else:
                # log error
                value = False
        
        return value
            
    
    question_deserialization_method = {
        'Person': SerializeForm.person_deserialize,
        'Address': SerializeForm.address_deserialize,
        'RadioButton': SerializeForm.radiobutton_deserialize,
        'Dropdown': SerializeForm.dropdown_deserialize
    }
    
    def deserialize_responses (self, responses, form, form_model_class, response_model_class, mode):
        response_object_list = []
        for response in responses:
            question_id = response['question_id']
            question = Question.objects.get(id=question_id)
            storage_id = getattr(response, 'storage_id', None)
            try:
                question_storage = QuestionStorage.objects.get(question = question)
                if question.answer_type.name in question_deserialization_method:
                    val = self.question_deserialization_method(response, question, false, mode)
                else:
                    val = getattr(response, 'value', None)
                    setattr(form, storage.field_name, val) 
            except:
                if response_model_class is not None:
                    if storage_id is None:
                        response_object = response_model_class()
                        response_object.parent = form
                        response_object.question = question
                    else:
                        response_object = response_model_class.objects.get(storage_id)
                        
                    if question.answer_type.name in question_deserialization_method:
                        response_object.value = self.question_deserialization_method(response, question, true, mode)
                    else:
                        response_object.value = getattr(response, 'value', None)
                        
                    response_object_list.append(response_object)
                else:
                    #log error, throw exception?
                    pass
        
        return response_object_list
    
    def deserialize_cards (self, cards, form, mode):
        objects_to_save = []
        for card in cards:
            category_id = card['category_id']
            card_storage = CardStorage.objects.get(category__id = category_id)
            storage = Storage.objects.get(id=card_storage.storage.id)
            storage = FormStorage.objects.get(form=form)
            mod = __import__(storage.module_name, fromlist=[storage.form_model_name, storage.response_model_name])
            card_model_class = getattr(mod, storage.form_model_name)
            if storage.response_model_name is not None:
                response_model_class = getattr(mod, storage.response_model_name, None)
            else:
                response_model_class = None
            
            instance_list = card['instances']
            for inst in instance_list:
                storage_id = getattr(inst, 'storage_id', None)
                if storage_id is None:
                    inst_object = card_model_class()
                    setattr(inst_object, storage.foreign_key_field_child, form)
                else:
                    inst_object = card_model_class.objects.get(id=storage_id)
                
                objects_to_save.append(inst_object)
                responses = inst['responses']
                objects_to_save += self.deserialize_responses(responses, inst_object, card_model_class, response_model_class)
        
        return objects_to_save            
    
    def deserialize(self, form_dict, mode):
        objects_to_save = []
        form = Form.objects.get(id=form_dict['form_id'])
        storage = FormStorage.objects.get(form=form)
        mod = __import__(storage.module_name, fromlist=[storage.form_model_name, storage.response_model_name])
        form_model_class = getattr(mod, storage.form_model_name)
        response_model_class = getattr(mod, storage.response_model_name, None)
        storage_id = form_dict.get('storage_id')
        if storage_id is None:
            form = form_class()
            station_id = form_dict['station_id']
            form.station = BorderStation.objects.get(id=station_id)
        else:
            form = form_class.objects.get(id=storage_id)
        
        objects_to_save.append(form)
        
        responses = form_dict['responses']
        objects_to_save += deserialize_responses(responses, form, form_model_class, response_model_class, mode)
        
        objects_to_save += deserialize_cards(cards, form, mode)
        
        
            
            