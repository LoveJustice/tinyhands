import logging

from django.db import transaction

from rest_framework import filters, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_api.authentication import HasPermission

from dataentry import fuzzy_matching
from dataentry.serializers import IDManagementSerializer, PersonFormsSerializer
from dataentry.models import AliasGroup, Person

logger = logging.getLogger(__name__)

class IDManagementViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = IDManagementSerializer
    permission_classes = (IsAuthenticated, HasPermission)
    permissions_required = ['permission_irf_edit', 'permission_vif_edit']
    filter_backends = (filters.SearchFilter, filters.OrderingFilter,)
    search_fields = ('full_name',)
    ordering_fields = ('full_name', 'age', 'gender', 'phone_contact','aliases',
            'form_type','form_number','form_date')
    ordering = ('full_name',)

    def fuzzy_match(self, request):
        input_name = request.GET['name']
        results = fuzzy_matching.match_person(input_name)
        serializer = IDManagementSerializer(results, many=True, context={'request': request})
        return Response(serializer.data)

    def partial_phone(self, request):
        input_phone = request.GET['phone']
        results = Person.objects.filter(phone_contact__contains=input_phone)
        serializer = IDManagementSerializer(results, many=True, context={'request': request})
        return Response(serializer.data)

    def person_forms(self, request):
        person_id = request.GET['person_id']
        person = Person.objects.get(id=person_id)
        forms = person.get_form_data()
        serializer = PersonFormsSerializer(forms, many=True, context={'request': request})
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

