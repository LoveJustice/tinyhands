import json
import traceback
import logging
from datetime import date
from datetime import datetime

from rest_framework import filters as fs
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_api.authentication import HasPermission
from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models import Q

from dataentry.models import MasterPerson, PersonBoxCommon, PersonPhone, PersonAddress, PersonSocialMedia, PersonDocument, PersonMatch, MatchType
from dataentry.models import MatchHistory, MatchAction, UserLocationPermission
from dataentry.models.pending_match import PendingMatch
from dataentry.serializers import MasterPersonSerializer, PersonAddressSerializer, PersonMatchSerializer, PersonPhoneSerializer, PersonSocialMediaSerializer, PersonDocumentSerializer, PersonInMasterSerializer

logger = logging.getLogger(__name__)

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
        perm_list = UserLocationPermission.objects.filter(account__id=request.user.id, permission__permission_group='PERSON_MANAGEMENT')
        if len(perm_list) < 1:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
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
                serializer.save()
                
                if ret is None:
                    ret = self.update_sub_model_list(PersonAddressSerializer, master_person.personaddress_set.all(), request_json.get('personaddress_set'), True)
                if ret is None: 
                    ret = self.update_sub_model_list(PersonPhoneSerializer, master_person.personphone_set.all(), request_json.get('personphone_set'), True)
                if ret is None:
                    self.update_sub_model_list(PersonSocialMediaSerializer, master_person.personsocialmedia_set.all(), request_json.get('personsocialmedia_set'), True)
                if ret is None:
                    self.update_sub_model_list(PersonDocumentSerializer, master_person.persondocument_set.all(), request_json.get('persondocument_set'), True)
                if ret is None:
                    self.update_sub_model_list(PersonInMasterSerializer, master_person.person_set.all(), request_json.get('person_set'), False)
                
                if ret is not None:
                    transaction.rollback()
                    transaction.set_autocommit(True)
                    rtn_status = status.HTTP_400_BAD_REQUEST
                else:
                    transaction.commit()
                    transaction.set_autocommit(True)
                    updated_master_person = MasterPerson.objects.get(id=pk)
                    serializer2 = self.serializer_class(updated_master_person, context={'request': request})
                    ret = serializer2.data
                    rtn_status = status.HTTP_200_OK
            else:
                transaction.rollback()
                transaction.set_autocommit(True)
                ret = serializer.errors
                rtn_status = status.HTTP_400_BAD_REQUEST
        
        except:
            transaction.rollback()
            transaction.set_autocommit(True)
            ret = {
                'errors': 'Internal Error:' + traceback.format_exc(),
                'warnings':[]
                }
            rtn_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        
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
        
        perm_list = UserLocationPermission.objects.filter(account__id=request.user.id, permission__permission_group='PERSON_MANAGEMENT')
        if len(perm_list) < 1:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
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
        
        perm_list = UserLocationPermission.objects.filter(account__id=request.user.id, permission__permission_group='PERSON_MANAGEMENT')
        if len(perm_list) < 1:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        notes = request.data.get('notes', '')
        transaction.set_autocommit(False)
        try:
            new_master = MasterPerson()
            new_master.update(person)
            new_master.save()
            person.master_person = new_master
            person.master_set_notes = notes
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
            
            match_history = MatchHistory()
            match_history.master1 = master
            match_history.master2 = None
            match_history.person = person
            match_history.notes = notes 
            match_history.match_type = None
            match_history.action = MatchAction.objects.get(name='remove from master person')
            match_history.matched_by = request.user
            match_history.timstamp = datetime.now()
            match_history.save()
            
            match_history = MatchHistory()
            match_history.master1 = master
            match_history.master2 = None
            match_history.person = None
            match_history.notes = notes 
            match_history.match_type = None
            match_history.action = MatchAction.objects.get(name='create master person')
            match_history.matched_by = request.user
            match_history.timstamp = datetime.now()
            match_history.save()
            
            match_history = MatchHistory()
            match_history.master1 = new_master
            match_history.master2 = None
            match_history.person = person
            match_history.notes = notes 
            match_history.match_type = None
            match_history.action = MatchAction.objects.get(name='add to master person')
            match_history.matched_by = request.user
            match_history.timstamp = datetime.now()
            match_history.save()
            
            serializer = self.serializer_class(master, context={'request': request})
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
            

    def retrieve_matches(self, request, id, type_id):
        matches = []
        perm_list = UserLocationPermission.objects.filter(account__id=request.user.id, permission__permission_group='PERSON_MANAGEMENT')
        if len(perm_list) < 1:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        results = PersonMatch.objects.filter(Q(master1__id=id) | Q(master2__id=id), match_type__id=type_id)
        for result in results:
            match = {
                'id':result.id,
                'match_type':type_id,
                'match_date':result.match_date,
                'notes':result.notes,
                }
            if result.matched_by is None:
                match['matched_by'] = ''
            else:
                match['matched_by'] = result.matched_by.get_full_name()
            if result.master1.id == int(id):
                serializer = self.serializer_class(result.master2, context={'request': request})
            else:
                serializer = self.serializer_class(result.master1, context={'request': request})
            
            match['master_person'] = serializer.data
            matches.append(match)
        
        return Response (matches)
    
    def update_match(self, request, id):
        perm_list = UserLocationPermission.objects.filter(account__id=request.user.id, permission__permission_group='PERSON_MANAGEMENT')
        if len(perm_list) < 1:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        person_match = PersonMatch.objects.get(id=id)
        tmp = request.data.get('match_type')
        match_type = MatchType.objects.get(id=tmp)
        person_match.match_type = match_type
        person_match.notes = request.data.get('notes','')
        person_match.match_date = date.today()
        person_match.matched_by = request.user
        person_match.save()
        
        match_history = MatchHistory()
        match_history.master1 = person_match.master1
        match_history.master2 = person_match.master2
        match_history.person = None
        match_history.notes = request.data.get('notes','')
        match_history.match_type = match_type
        match_history.action = MatchAction.objects.get(name='update match')
        match_history.matched_by = request.user
        match_history.timstamp = datetime.now()
        match_history.save()
        return Response({}, status.HTTP_200_OK)
    
    @staticmethod
    def create_match_base(user, data):
        person_match = PersonMatch()
        tmp = data.get('match_type')
        match_type = MatchType.objects.get(id=tmp)
        tmp = data.get('master1')
        person_match.master1 = MasterPerson.objects.get(id=tmp)
        tmp = data.get('master2')
        person_match.master2 = MasterPerson.objects.get(id=tmp)
        person_match.match_type = match_type
        person_match.notes = data.get('notes','')
        person_match.match_date = date.today()
        person_match.matched_by = user
        person_match.save()
        
        match_history = MatchHistory()
        match_history.master1 = person_match.master1
        match_history.master2 = person_match.master2
        match_history.person = None
        match_history.notes = data.get('notes','')
        match_history.match_type = match_type
        match_history.action = MatchAction.objects.get(name='create match')
        match_history.matched_by = user
        match_history.timstamp = datetime.now()
        match_history.save()
    
    def create_match(self, request):
        perm_list = UserLocationPermission.objects.filter(account__id=request.user.id, permission__permission_group='PERSON_MANAGEMENT')
        if len(perm_list) < 1:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        MasterPersonViewSet.create_match_base(request.user, request.data)
        return Response({}, status.HTTP_200_OK)
    
    @staticmethod
    def merge_master_persons_base(id1, id2, user, data):
        master1 = MasterPerson.objects.get(id=id1)
        master2 = MasterPerson.objects.get(id=id2)
        
        
        try:
            master1.full_name = data['full_name']
            master1.birthdate = data['birthdate']
            master1.estimated_birthdate = data['estimated_birthdate']
            master1.gender = data['gender']
            master1.nationality = data['nationality']
            if len(master1.appearance) < 1:
                master1.appearance = master2.appearance
            else:
                master1.appearance = "\n" + master2.appearance
            if len(master1.notes) < 1:
                master1.notes = master2.notes
            else:
                master1.notes += "\n" + master2.notes
            master1.save()
            
            for address in master2.personaddress_set.all():
                address.master_person = master1
                address.save()
        
            for phone in master2.personphone_set.all():
                phone.master_person = master1
                phone.save()
            
            for social in master2.personsocialmedia_set.all():
                social.master_person = master1
                social.save()
            
            for document in master2.persondocument_set.all():
                document.master_person = master1
                document.save()
            
            param_notes = data['notes']
            for person in master2.person_set.all():
                person.master_person = master1
                person.master_set_notes = param_notes
                person.master_set_date = date.today()
                person.master_set_by = user
                person.save()
                
                match_history = MatchHistory()
                match_history.master1 = master2
                match_history.master2 = None
                match_history.person = person
                match_history.notes = param_notes
                match_history.match_type = None
                match_history.action = MatchAction.objects.get(name='remove from master person')
                match_history.matched_by = user
                match_history.timstamp = datetime.now()
                match_history.save()
                
                match_history = MatchHistory()
                match_history.master1 = master1
                match_history.master2 = None
                match_history.person = person
                match_history.notes = param_notes
                match_history.match_type = None
                match_history.action = MatchAction.objects.get(name='add to master person')
                match_history.matched_by = user
                match_history.timstamp = datetime.now()
                match_history.save()
                
            master2.active = False
            master2.save()
            
            results = PersonMatch.objects.filter(Q(master1=master2) | Q(master2=master2))
            for match in results:
                match.delete()
            
            match_history = MatchHistory()
            match_history.master1 = master1
            match_history.master2 = master2
            match_history.person = None
            match_history.notes = param_notes
            match_history.match_type = None
            match_history.action = MatchAction.objects.get(name='merge master persons')
            match_history.matched_by = user
            match_history.timstamp = datetime.now()
            match_history.save()
            
            match_history = MatchHistory()
            match_history.master1 = master2
            match_history.master2 = None
            match_history.person = None
            match_history.notes = param_notes
            match_history.match_type = None
            match_history.action = MatchAction.objects.get(name='deactivate master person')
            match_history.matched_by = user
            match_history.timstamp = datetime.now()
            match_history.save()
            
            transaction.commit()
            rtn_status = status.HTTP_200_OK
            ret = {
                'master':master1
                }
        except:
            logger.error(traceback.format_exc())
            transaction.rollback()
            ret = {
                'errors': 'Internal Error:' + traceback.format_exc(),
                'warnings':[],
                'master': None
                }
            rtn_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        
        return {
            'ret':ret,
            'status':rtn_status
            }
        
    def merge_master_persons(self, request, id1, id2):
        perm_list = UserLocationPermission.objects.filter(account__id=request.user.id, permission__permission_group='PERSON_MANAGEMENT')
        if len(perm_list) < 1:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        transaction.set_autocommit(False)
        result = MasterPersonViewSet.merge_master_persons_base(id1, id2, request.user, request.data)
        transaction.set_autocommit(True)
        
        if result['ret']['master'] is not None:
            serializer = self.serializer_class(result['ret']['master'], context={'request': request})
            result['ret'] = serializer.data
        
        return Response (result['ret'], status=result['status'])
        
class PendingMatchViewSet(viewsets.ModelViewSet):
    serializer_class = PersonMatchSerializer
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ('person_match__master1__full_name','person_match__master2__full_name')
    ordering_fields = ('person_match__master1__full_name','person_match__master2__full_name')
    ordering = ('person_match__master1__full_name',)
    
    def get_queryset(self):
        queryset = PendingMatch.objects.all()
        in_country = self.request.GET.get('country')
        if in_country is not None:
            queryset = queryset.filter(country__id=in_country)
        match_type = self.request.GET.get('match')
        if match_type is not None:
            queryset = queryset.filter(person_match__match_type__name=match_type)
        return queryset
        