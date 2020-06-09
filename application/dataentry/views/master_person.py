import json
import traceback

from rest_framework import filters as fs
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_api.authentication import HasPermission
from django.core.files.storage import default_storage
from django.db import transaction

from dataentry.models import MasterPerson, PersonBoxCommon, PersonPhone, PersonAddress, PersonSocialMedia, PersonDocument
from dataentry.serializers import MasterPersonSerializer, PersonAddressSerializer, PersonPhoneSerializer, PersonSocialMediaSerializer, PersonDocumentSerializer, PersonInMasterSerializer

class MasterPersonViewSet(viewsets.ModelViewSet):
    parser_classes = (MultiPartParser,FormParser,JSONParser)
    queryset = MasterPerson.objects.all()
    serializer_class = MasterPersonSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ('full_name',)
    ordering_fields = ('full_name',)
    ordering = ('full_name',)
    
    def update_sub_model_list(self, serializer_class, prior_list, data, allow_delete, allow_update=True):
        delete_list = []
        modified = {}
        new_list = []
        
        if data is not None:
            for element in data:
                if element.get('id') is not None:
                    modified[element.get('id')] = element
                else:
                    new_list.append(element)
        
        for element in prior_list:
            if element.id in modified:
                if allow_update:
                    serializer = serializer_class(element, data=modified[element.id])
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        return serializer.errors
            else:
                delete_list.append(element)
        
        if allow_delete:
            for element in delete_list:
                element.delete()
        
        for element in new_list:
            serializer = serializer_class(data=element)
            if serializer.is_valid():
                serializer.save()
            else:
                return serializer.errors
        
        return None
    
    def update(self, request, pk):
        request_string = request.data['main']
        request_json = json.loads(request_string)
        
        cnt = 0;
        while 'document[' + str(cnt) + ']' in request.data:
            upload = request.data['document[' + str(cnt) + ']']
            filename = upload.name
            cnt += 1
            with default_storage.open('person_documents/' + filename, 'wb+') as destination:
                for chunk in upload.chunks():
                    destination.write(chunk)
        
        
        master_person = MasterPerson.objects.get(id=pk)

        transaction.set_autocommit(False)
        try:
            serializer = MasterPersonSerializer(master_person, data=request_json)
            ret = None
            rtn_status = None
            if serializer.is_valid():
                updated_master_person = serializer.save()
                
                if ret is None:
                    ret = self.update_sub_model_list(PersonAddressSerializer, master_person.personaddress_set.all(), request_json.get('personaddress_set'), True)
                if ret is None: 
                    ret = self.update_sub_model_list(PersonPhoneSerializer, master_person.personphone_set.all(), request_json.get('personphone_set'), True)
                if ret is None:
                    self.update_sub_model_list(PersonSocialMediaSerializer, master_person.personsocialmedia_set.all(), request_json.get('personsocialmedia_set'), True)
                if ret is None:
                    self.update_sub_model_list(PersonDocumentSerializer, master_person.persondocument_set.all(), request_json.get('persondocument_set'), True, allow_update=False)
                if ret is None:
                    self.update_sub_model_list(PersonInMasterSerializer, master_person.person_set.all(), request_json.get('person_set'), False)
                
                if ret is not None:
                    transaction.rollback()
                    rtn_status = status.HTTP_400_BAD_REQUEST
                else:
                    serializer2 = MasterPersonSerializer(updated_master_person)
                    ret = serializer2.data
                    transaction.commit()
                    rtn_status = status.HTTP_200_OK
            else:
                transaction.rollback()
                ret = serializer.errors
                rtn_status = status.HTTP_400_BAD_REQUEST
        
        except:
            transaction.rollback()
            ret = {
                'errors': 'Internal Error:' + traceback.format_exc(),
                'warnings':[]
                }
            rtn_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        
        transaction.set_autocommit(True)
        return Response (ret, status=rtn_status)
    
    def retrieve_type(self, request, type_name):
        mod = __import__('dataentry.models.master_person', fromlist=[type_name])
        type_class = getattr(mod, type_name, None)
        data = []
        if type_class is not None:
            type_values = type_class.objects.all().order_by('name')
            for type_value in type_values:
                data.append({'id':type_value.id, 'name':type_value.name})
        
        return Response(data)
    
    def retrieve_pv_relations(self, request, id):
        relations = []
        master = MasterPerson.objects.get(id=id)
        persons = master.person_set.all()
        
        pbs = PersonBoxCommon.objects.filter(person__in=persons)
        for pb in pbs:
            if pb.relation_to_pv is not None and pb.relation_to_pv != '':
                found = False
                for relation in relations: 
                    if relation['relation'] == pb.relation_to_pv:
                        relation['count'] += 1
                        found = True
                
                if not found:
                    relations.append({'relation':pb.relation_to_pv, 'count':1})
        
        return Response(relations)
    
    def remove_person(self, request, id, person_id):
        master = MasterPerson.objects.get(id=id)
        person = master.person_set.get(id=person_id)
        
        transaction.set_autocommit(False)
        try:
            new_master = MasterPerson()
            new_master.update(person)
            new_master.save()
            person.master_person = new_master
            person.save()
            
            for phone in master.personphone_set.all():
                new_phone = PersonPhone()
                new_phone.master_person = new_master
                for field in ['number','phone_verified','phone_type']:
                    setattr(new_phone, field, getattr(phone, field))
                new_phone.save()
            
            for address in master.personaddress_set.all():
                new_address = PersonAddress()
                new_address.master_person = new_master
                for field in ['address','latitude','longitude','address_notes','address_verified','address_type']:
                    setattr(new_address, field, getattr(address, field))
                new_address.save()
                
            for social in master.personsocialmedia_set.all():
                new_social = PersonPhone()
                new_social.master_person = new_master
                for field in ['social_media','social_media_verified','social_media_type']:
                    setattr(new_social, field, getattr(social, field))
                new_social.save()
            
            for document in master.persondocument_set.all():
                new_document = PersonDocument()
                new_document.master_person = new_master
                for field in ['file_location','document_type']:
                    setattr(new_document, field, getattr(document, field))
                new_document.save()
            
            serializer = MasterPersonSerializer(master)
            ret = serializer.data
            transaction.commit()
            rtn_status = status.HTTP_200_OK
        except:
            transaction.rollback()
            ret = {
                'errors': 'Internal Error:' + traceback.format_exc(),
                'warnings':[]
                }
            rtn_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        
        return Response (ret, status=rtn_status)
            

    def retrieve_matches(self, request, id):
        pass
        