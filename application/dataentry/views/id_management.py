import logging

from django.db import transaction

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_api.authentication import HasPermission
from rest_framework import filters as fs
from itertools import chain


from dataentry import fuzzy_matching
from dataentry.serializers import IDManagementSerializer, PersonFormsSerializer
from dataentry.models import AliasGroup, Person, PersonFormCache, Interceptee, VictimInterview

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
        results = Person.objects.filter(alias_group=group_id);
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
            alias_group = None
            if person1.alias_group is not None:
                alias_group = person1.alias_group

            if person2.alias_group is not None:
                if alias_group is not None:
                    logger.error("Cannot make alias group from two persons where both are already in alias groups")
                    return Response({'detail': "Both persons already in alias group"}, status=status.HTTP_409_CONFLICT)
                alias_group = person2.alias_group

            with transaction.atomic():
                if alias_group is None:
                    alias_group = AliasGroup()
                    alias_group.save()

                person1.alias_group = alias_group
                person1.save()
                person2.alias_group = alias_group
                person2.save()
        except BaseException:
            logger.error('Failed to add to alias group: ' + pk + ' ' + pk2)
            return Response({'detail': "an error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "success!"})

    def remove_alias_group (self, request, pk):
        try:
            person = Person.objects.get(id=pk)
            if person.alias_group is None:
                return
        except ObjectDoesNotExist:
            logger.error('Failed to remove from alias group: ' + pk)
            return Response({'detail': "an error occurred"}, status=status.HTTP_404_NOT_FOUND)

        try:
            with transaction.atomic():
                alias_group = person.alias_group
                person.alias_group = None
                person.save()

                # check remaining members of the group
                members = Person.objects.filter(alias_group = alias_group)
                if len(members) < 2:
                    # only one member left in the alias group - delete the alias group
                    for member in members:
                        member.alias_group = None
                        member.save()
                    alias_group.delete()
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
        if 'exclude' in request.GET:
            excludes = request.GET['exclude']
        else:
            excludes = ''
        results = fuzzy_matching.match_person(input_name, excludes)
        serializer = IDManagementSerializer(results, many=True, context={'request': request})
        return Response(serializer.data)

    def partial_phone(self, request):
        input_phone = request.GET['phone']
        victim_ids = []
        if 'exclude' in request.GET:
            excludes = request.GET['exclude']
            if excludes != None and excludes == 'victims':
                irf_victim_ids = Interceptee.objects.filter(kind = 'v').values_list('person', flat=True)
                vif_victim_ids = VictimInterview.objects.all().values_list('victim', flat=True)
                victim_ids = list(chain(irf_victim_ids, vif_victim_ids))
            
        results = Person.objects.filter(phone_contact__contains=input_phone).exclude(id__in = victim_ids)
        serializer = IDManagementSerializer(results, many=True, context={'request': request})
        return Response(serializer.data)