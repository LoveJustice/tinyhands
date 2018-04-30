import json
from rest_framework import viewsets
from rest_framework.response import Response

from braces.views import LoginRequiredMixin
from accounts.mixins import PermissionsRequiredMixin

from django.views.generic import CreateView
from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet
from dataentry.serialize_form import FormDataSerializer

from dataentry.form_data import Form, FormData



class IrfFormViewSet(viewsets.GenericViewSet):
    
    def retrieve(self, request, country_id, pk):
        form = Form.objects.get(form_type__name='IRF', country__id=country_id)
        irf = FormData.find_object_by_id(pk, form)
        form_data = FormData(irf, form)
        serializer = FormDataSerializer(form_data)
       
        return Response(serializer.data)
    
    def not_called(self):
        serializer2 = FormDataSerializer(data=serializer.data, context={'form_type':form.form_type, 'mode':'IRF', 'clear_storage_id':True})
        serializer2.is_valid()
        form_data2 = serializer2.get_or_create()
        form_data2.form_object.irf_number = 'MBZ951'
        form_data2.save_object()
        
        serializer3 = FormDataSerializer(form_data2)
        
        print (serializer.data)
        print (serializer3.data)
