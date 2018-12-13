from rest_framework import filters as fs
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_api.authentication import HasPermission, HasDeletePermission, HasPostPermission

from dataentry.models import CardStorage, Form, Person, Question
from dataentry.serializers import PersonSerializer
from dataentry.serialize_form import ResponsePersonSerializer

class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = (IsAuthenticated, HasPermission)
    permissions_required = ['permission_address2_manage']
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ('full_name',)
    ordering_fields = ('full_name', 'age', 'gender', 'phone_contact')
    ordering = ('full_name',)
    
    def associated_persons(self, request, station_id, form_number):
        kind = request.GET.get('kind', None)
        irf_number = form_number
        while irf_number[-1].isalpha():
            irf_number = irf_number[:-1]
            
        form = Form.current_form('IRF',station_id)
        card_storages = CardStorage.objects.filter(category__name='Interceptees', category__form = form)
        persons_data = []
        if len(card_storages) > 0:
            storage = card_storages[0].storage
            mod = __import__(storage.module_name, fromlist=[storage.form_model_name])
            interceptee_class = getattr(mod, storage.form_model_name)
            
            interceptees = interceptee_class.objects.filter(interception_record__irf_number=irf_number)
            if kind is not None:
                interceptees = interceptees.filter(kind=kind)
            person_ids = []
            for interceptee in interceptees:
                if interceptee.person is not None:
                    person_ids.append(interceptee.person.id)
                    
            persons = Person.objects.filter(id__in=person_ids)
            
            serializer = ResponsePersonSerializer(persons, many=True, context={'question':Question()})
            persons_data = serializer.data
        return Response(persons_data)

        