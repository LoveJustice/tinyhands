from rest_framework import filters as fs
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist

from dataentry.models import Incident, IntercepteeCommon, LocationForm, LocationInformation, Suspect, SuspectInformation, VdfCommon
from dataentry.serializers import IncidentSerializer

class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ('incident_number',)
    ordering_fields = ('incident_number', 'incident_date',)
    ordering = ('-incident_date',)
    
    @staticmethod
    def is_matching_form(form_number, incident_number):
        is_match = False
            
        if form_number.startswith(incident_number):
            is_match = True
            if form_number[len(incident_number)] == '.':
                for idx in range(len(incident_number)+1, len(form_number)):
                    if form_number[idx] < '0' or form_number[idx] > '9':
                        is_match = False
                        break
            else:     
                for idx in range(len(incident_number),len(form_number)):
                    if form_number[idx] < 'A' or form_number[idx] > 'Z':
                        is_match = False
                        break
        return is_match
        

    def get_names_and_addresses(self, request):
        incident_numbers_string = request.GET.get('number', None)
        
        
        names = {
                'address':{
                    'forms':[],
                    'irfs':[],      # irfs will always be empty
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
            
            pvfs = VdfCommon.objects.filter(vdf_number__startswith=incident_number)
            for pvf in pvfs:
                if pvf.victim is not None and IncidentViewSet.is_matching_form(pvf.vdf_number, incident_number):
                    names['pv']['forms'].append({'text':pvf.victim.full_name, 'title':'PVF ' + pvf.vdf_number})
            
            sfs = Suspect.objects.filter(sf_number__startswith=incident_number)
            for sf in sfs:
                if sf.merged_person is not None and IncidentViewSet.is_matching_form(sf.sf_number, incident_number):
                    names['suspect']['forms'].append({'text':sf.merged_person.full_name, 'title':'SF ' + sf.sf_number})
            
            suspect_infos = SuspectInformation.objects.filter(incident__incident_number=incident_number)
            for suspect_info in suspect_infos:
                names['suspect']['forms'].append({'text':suspect_info.person.full_name, 'title':'SF ' + suspect_info.suspect.sf_number})  
            
            lfs =  LocationForm.objects.filter(lf_number__startswith=incident_number)
            for lf in lfs:
                if lf.merged_address is not None and 'address' in lf.merged_address and IncidentViewSet.is_matching_form(lf.lf_number, incident_number):
                    names['address']['forms'].append({'text':lf.merged_address['address'], 'title':'LF ' + lf.lf_number})
            
            location_infos = LocationInformation.objects.filter(incident__incident_number = incident_number)
            for location_info in location_infos:
                if location_info.address is not None and 'address' in location_info.address:
                    names['address']['forms'].append({'text':location_info.address['address'], 'title':'LF ' + lf.lf_number})
                

        return Response(names)