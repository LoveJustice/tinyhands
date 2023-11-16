from rest_framework import viewsets
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import date
import json

from dataentry.models import Incident, IntercepteeCommon, IrfCommon, LocationForm, MasterPerson, Person, Suspect, VdfCommon, BorderStation, IrfAttachmentCommon, VdfAttachmentCommon, SuspectAttachment, LocationAttachment
from django.core.files.storage import default_storage

class MonitorAppViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    
    def create(self, request):
        form_type = request.data['formType']
        request_string = request.data['main']
        request_json = json.loads(request_string)
        if form_type == 'IRF':
            return self.create_irf(request, request_json)
        elif form_type =='PVF':
            return self.create_pvf(request, request_json)
        elif form_type =='SF':
            return self.create_sf(request, request_json)
        elif form_type =='LF':
            return self.create_lf(request, request_json)
        else:
            pass
    
    def add_file(self, request, name, path):
        if name is not None:
            file_obj = request.FILES.get(name)
            if file_obj:
                with default_storage.open(path, 'wb+') as destination:
                    for chunk in file_obj.chunks():
                        destination.write(chunk)
    
    def incident_from_form_number(self, form_number, station):
        base_number = form_number
        for idx in range(len(station.station_code), len(form_number)):
            if (form_number[idx] < '0' or form_number[idx] > '9') and form_number[idx] != '_':
                base_number = form_number[:idx]
                break
        
        return base_number
        
    def create_irf(self, request, request_json):
        form_number = request_json['formNumber']
        existing_irf = IrfCommon.objects.filter(irf_number=form_number)
        if existing_irf.exists():
            return Response("Duplicate Form", status.HTTP_409_CONFLICT)

        border_station = BorderStation.objects.get(station_code=form_number[0:3])
        incident_number = self.incident_from_form_number(form_number, border_station)
        try:
            incident = Incident.objects.get(incident_number=incident_number)
        except:
            incident = Incident()
            incident.incident_number = form_number
            incident.incident_date = date.today()
            incident.summary = 'Created by Monitor App'
            incident.station = border_station
            incident.save()

        irf = IrfCommon()
        irf.station = border_station
        irf.irf_number = form_number
        irf.date_of_interception = date.today()
        irf.status = 'in-progress'
        irf.save()
        
        people = request_json['people']
        for index, person in enumerate(people):
            name = person['name']
            person_type = person['personType']

            file_name = person['file']
            if file_name == 'null':
                file_path = None
            else:
                file_path = 'interceptee_photos/' + file_name
                file_key = f'people[{index}][file]'
                self.add_file(request, file_key, file_path)
            
            master = MasterPerson()
            master.full_name = name
            master.kind = person_type
            master.save()
            
            person = Person()
            person.full_name = name
            person.role = person_type
            person.photo = file_path
            person.master_person = master
            person.save()
            
            interceptee = IntercepteeCommon()
            interceptee.interception_record = irf
            interceptee.person = person
            interceptee.save()

        pdfs = request_json['pdfs']
        for index, pdf in enumerate(pdfs):
            document_type = pdf['documentType']
            file_name = pdf['file']
            if file_name == 'null':
                file_path = None
            else:
                file_path = 'scanned_irf_forms/' + file_name
                file_key = f'pdfs[{index}][file]'
                self.add_file(request, file_key, file_path)
            
            attach = IrfAttachmentCommon()
            attach.interception_record = irf
            attach.option = document_type
            attach.attachment = file_path
            attach.attachment_number = index + 1
            attach.save()
        
        return Response({"id": irf.id}, status.HTTP_200_OK)
            
    
    def create_pvf(self, request, request_json):
        form_number = request_json['formNumber']
        existing_pvf = VdfCommon.objects.filter(vdf_number=form_number)
        if existing_pvf.exists():
            return Response("Duplicate Form", status.HTTP_409_CONFLICT)

        border_station = BorderStation.objects.get(station_code=form_number[0:3])
        
        pvf = VdfCommon()
        pvf.vdf_number = form_number
        pvf.station = border_station
        pvf.status = 'in-progress'
        pvf.victim = None
        pvf.save()
        
        pdfs = request_json['pdfs']
        for index, pdf in enumerate(pdfs):
            document_type = pdf['documentType']
            file_name = pdf['file']
            if file_name == 'null':
                file_path = None
            else:
                file_path = 'vdf_attachments/' + file_name
                file_key = f'pdfs[{index}][file]'
                self.add_file(request, file_key, file_path)

            attach = VdfAttachmentCommon()
            attach.vdf = pvf
            attach.option = document_type
            attach.attachment = file_path
            attach.attachment_number = index + 1
            attach.save()
        
        return Response({"id": pvf.id}, status.HTTP_200_OK)
    
    def create_sf(self, request, request_json):
        form_number = request_json['formNumber']
        existing_sf = Suspect.objects.filter(sf_number=form_number)
        if existing_sf.exists():
            return Response("Duplicate Form", status.HTTP_409_CONFLICT)

        border_station = BorderStation.objects.get(station_code=form_number[0:3])
        incident_number = self.incident_from_form_number(form_number, border_station)
        incident = Incident.objects.get(incident_number=incident_number)

        sf = Suspect()
        sf.sf_number = form_number
        sf.station = border_station
        sf.status = 'in-progress'
        sf.merged_person = None
        sf.save()
        sf.incidents.add(incident)

        pdfs = request_json['pdfs']
        for index, pdf in enumerate(pdfs):
            document_type = pdf['documentType']
            file_name = pdf['file']
            if file_name == 'null':
                file_path = None
            else:
                file_path = 'sf_attachments/' + file_name
                file_key = f'pdfs[{index}][file]'
                self.add_file(request, file_key, file_path)

            attach = SuspectAttachment()
            attach.suspect = sf
            attach.option = document_type
            attach.attachment = file_path
            attach.attachment_number = index + 1
            attach.save()
        
        return Response({"id": sf.id}, status.HTTP_200_OK)
    
    def create_lf(self, request, request_json):
        form_number = request_json['formNumber']
        existing_lf = LocationForm.objects.filter(lf_number=form_number)
        if existing_lf.exists():
            return Response("Duplicate Form", status.HTTP_409_CONFLICT)

        border_station = BorderStation.objects.get(station_code=form_number[0:3])
        incident_number = self.incident_from_form_number(form_number, border_station)
        incident = Incident.objects.get(incident_number=incident_number)
        
        lf = LocationForm()
        lf.incident = incident
        lf.lf_number = form_number
        lf.station = border_station
        lf.status = 'in-progress'
        lf.merged_place = ''
        lf.save()
        
        pdfs = request_json['pdfs']
        for index, pdf in enumerate(pdfs):
            document_type = pdf['documentType']
            file_name = pdf['file']
            if file_name == 'null':
                file_path = None
            else:
                file_path = 'lf_attachments/' + file_name
                file_key = f'pdfs[{index}][file]'
                self.add_file(request, file_key, file_path)
            
            attach = LocationAttachment()
            attach.lf = lf
            attach.option = document_type
            attach.attachment = file_path
            attach.attachment_number = index + 1
            attach.save()
        
        return Response({"id": lf.id}, status.HTTP_200_OK)
        