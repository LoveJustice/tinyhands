import logging
import traceback

from django.db import transaction

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_api.authentication import HasPermission
from rest_framework import filters as fs
from itertools import chain

from dataentry import fuzzy_matching
from dataentry.serializers import IDManagementSerializer, PersonFormsSerializer
from dataentry.models import MasterPerson, Person, PersonFormCache, Interceptee, VictimInterview

logger = logging.getLogger(__name__)

class IDManagementViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = IDManagementSerializer
    permission_classes = (IsAuthenticated, HasPermission)
    permissions_required = ['permission_irf_edit', 'permission_vif_edit']
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ('full_name','phone_contact')
    ordering_fields = ('full_name', 'age', 'gender', 'phone_contact', 'address1__name', 'address2__name')
    ordering = ('full_name',)

    def person_forms(self, request):
        person_id = request.GET['person_id']
        person = Person.objects.get(id=person_id)
        person_forms = []
        forms = PersonFormCache.get_form_data(person)
        for form in forms:
            obj = form.get_detail_as_object()
            if obj is not None:
                person_forms.append(obj)
            
        serializer = PersonFormsSerializer(person_forms, many=True, context={'request': request})
        return Response(serializer.data)

    def alias_group(self, request):
        group_id = request.GET['group_id']
        results = Person.objects.filter(master_person__id=group_id);
        serializer = IDManagementSerializer(results, many=True, context={'request': request})
        return Response(serializer.data)

    def get_person(self, request):
        person_id = request.GET['person_id']
        person = Person.objects.get(id=person_id)
        serializer = IDManagementSerializer(person, context={'request': request})
        return Response(serializer.data)

    def add_alias_group(self, request, pk, pk2):
        try:
            person1 = Person.objects.get(id=pk)
            person2 = Person.objects.get(id=pk2)
        except ObjectDoesNotExist:
            logger.error('Failed to add to alias group: ' + pk + ' ' + pk2)
            return Response({'detail': "an error occurred"}, status=status.HTTP_404_NOT_FOUND)

        try:
            master1 = person1.master_person
            master2 = person2.master_person
            
            with transaction.atomic():
                members = Person.objects.filter(master_person=master2)
                for member in members:
                    member.master_person = master1
                    member.save()
                    master1.update(member)
                
                master1.save() 
                master2.delete()
            
        except BaseException:
            logger.error('Failed to add to alias group: ' + pk + ' ' + pk2)
            return Response({'detail': "an error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "success!"})

    def remove_alias_group (self, request, pk):
        try:
            person = Person.objects.get(id=pk)
            if person.master_person is None:
                return
        except ObjectDoesNotExist:
            logger.error('Failed to remove from alias group: ' + pk)
            return Response({'detail': "an error occurred"}, status=status.HTTP_404_NOT_FOUND)

        try:
            with transaction.atomic():
                master = person.master_person
                master_person = MasterPerson()
                master_person.update(person)
                master_person.save()
                person.master_person = master_person
                person.save()

                # check remaining members of the group
                members = Person.objects.filter(master_person = master)
                if len(members) < 1:
                    master.delete()
        except BaseException:
            logger.error('Failed to remove from alias group: ' + pk)
            return Response({'detail': "an error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "success!"})


class TraffickerCheckViewSet(viewsets.ViewSet):
    serializer_class = IDManagementSerializer
    permission_classes = (IsAuthenticated, HasPermission)
    permissions_required = ['permission_person_match']
    
    def fuzzy_match(self, request):
        input_name = request.GET['name']
        if 'filter' in request.GET:
            filter = request.GET['filter']
        else:
            filter = ''
        results = fuzzy_matching.match_person(input_name, filter)
        serializer = IDManagementSerializer(results, many=True, context={'request': request})
        return Response(serializer.data)

    def partial_phone(self, request):
        input_phone = request.GET['phone']
        victim_ids = []
        if 'filter' in request.GET:
            filter = request.GET['filter']
            if filter is not None and filter == 'PVOT':
                victim_ids = fuzzy_matching.pvot_ids()
                results = Person.objects.filter(phone_contact__contains=input_phone, id__in=victim_ids)
            elif filter is not None and filter == 'Suspect':
                suspect_ids = fuzzy_matching.suspect_ids()
                results = Person.objects.filter(phone_contact__contains=input_phone, id__in=suspect_ids)
            else:
                results = Person.objects.filter(phone_contact__contains=input_phone)
        else:
            results = Person.objects.filter(phone_contact__contains=input_phone)
            
        serializer = IDManagementSerializer(results, many=True, context={'request': request})
        return Response(serializer.data)