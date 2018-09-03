from rest_framework import viewsets, status
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist

from dataentry.models import BorderStation, Form, FormType
from dataentry.serializers import FormSerializer, FormTypeSerializer

class FormTypeViewSet(viewsets.ModelViewSet):
    queryset = FormType.objects.all()
    serializer_class = FormTypeSerializer
    ordering = ('name',)
    
class FormViewSet(viewsets.ModelViewSet):
    queryset = Form.objects.all()
    serializer_class = FormSerializer
    ordering = ('form_type__name','name',)
    
    def list(self, request):
        form_qs = self.queryset
        if 'type_name' in request.GET:
            form_qs = form_qs.filter(form_type__name=request.GET['type_name'])
        if 'station_id' in request.GET:
            form_qs = form_qs.filter(stations__id = request.GET['station_id'])
        serializer = self.get_serializer(form_qs, many=True)
        return Response(serializer.data)
    
    def set_forms(self, request, station_id):
        try:
            station = BorderStation.objects.get(id=station_id)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        current_forms = self.queryset.filter(stations = station)
         
        remove_forms = []    
        for current_form in current_forms:
            found = False
            for new_form in request.data:
                if new_form == current_form.id:
                    found = True
                    break
        
            if not found:
                remove_forms.append(current_form)
        
        add_forms = []        
        for new_form in request.data:
            found = False
            for current_form in current_forms:
                if new_form == current_form.id:
                    found = True
                    break
                
            if not found:
                try:
                    the_form = Form.objects.get(id=new_form)
                    add_forms.append(the_form)
                except ObjectDoesNotExist:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
        
        for the_form in remove_forms:
            the_form.stations.remove(station)
        
        for the_form in add_forms:
            the_form.stations.add(station)
                
        return Response(request.data, status=status.HTTP_200_OK)
        