from rest_framework import filters as fs
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist

from dataentry.models import Incident, IntercepteeCommon
from dataentry.serializers import IncidentSerializer

class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ('incident_number',)
    ordering_fields = ('incident_number', 'incident_date',)
    ordering = ('-incident_date',)

    def get_names_and_addresses(self, request):
        incident_numbers_string = request.GET.get('number', None)
        
        
        names = {
                'address':{
                    'forms':[],
                    'locals':[]
                },
                'pv':{
                    'forms':[],
                    'irfs':[],
                    'locals':[]
                },
                'suspect':{
                    'forms':[],
                    'irfs':[],
                    'locals':[]
                }
            }
        
        incident_numbers = incident_numbers_string.split(',')
        for incident_number in incident_numbers:
            try:
                incident = Incident.objects.get(incident_number=incident_number)
           
                try:
                    interceptees = IntercepteeCommon.objects.filter(interception_record__irf_number=incident_number)
                    for interceptee in interceptees:
                        if interceptee.person.role == 'Suspect':
                            names['suspect']['irfs'].append({'text':interceptee.person.full_name, 'title':'IRF ' + interceptee.interception_record.irf_number});
                            pass
                        elif interceptee.person.role == 'PVOT':
                            names['pv']['irfs'].append({'text':interceptee.person.full_name, 'title':'IRF ' + interceptee.interception_record.irf_number});
                except ObjectDoesNotExist:
                    pass
            except ObjectDoesNotExist:
                pass

        return Response(names)