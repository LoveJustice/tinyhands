from rest_framework import viewsets
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from dataentry.models import Incident, IntercepteeCommon, IrfCommon, LocationForm, MasterPerson, Person, Suspect, VdfCommon

class MonitorAppViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated)
    
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
    
    def add_file(request, name, path):
        if name is not None:
            file_obj = request[name]
            with default_storage.open(path + name, 'wb+') as destination:
                for chunk in file_obj.chunks():
                    destination.write(chunk)
    
    def incident_from_form_number(self, form_number):
        base_number = form_number
        for idx in range(len(station.station_code), len(form_number)):
            if (form_number[idx] < '0' or form_number[idx] > '9') and form_number[idx] != '_':
                base_number = form_number[:idx]
                break
        
        return base_number
        
    def create_irf(self, request, request_json):
        form_number = request_json['formNumber']
        border_station = BorderStation.objects.get(station_code=form_number[0:3])
        incident_number = self.incident_from_form_number(form_number)
        
        try:
            incident = Incident.objects.get(incident_number=incident_number)
        except:
            incident = Incident()
            incident.incident_number = form_number
            incident.incident_date = date.today()
            incident.summary = 'Created by Monitor App'
            incident.save()
            
        irf = IrfCommon()
        irf.station = border_station
        irf.irf_number = form_number
        irf.date_of_interception = date.today()
        irf.status = 'in-progress'
        irf.save()
        
        people = request_json['people']
        for person in people:
            name = person['name']
            person_type = person['personType']
            file = person['file']
            if file == 'null':
                file = None
            self.add_file(request, file, 'interceptee_photos/')
            
            master = Person()
            master.full_name = name
            master.kind = person_type
            master.save()
            
            person_object = Person()
            person.full_name = name
            person.kind = person_type
            person.photo = file
            person.master_person = person
            person.save()
            
            interceptee = IntercepteeCommon()
            interceptee.interception_record = irf
            interceptee.person = person
            interceptee.save()
        
        next_number = 0
        pdfs = request_json['pdfs']
        for pdf in pdfs:
            document_type = pdf['documentType']
            file = pdf['file']
            self.add_file(request, file, 'scanned_irf_forms/')
            next_number += 1
            
            attach = IrfAttachmentCommon()
            attach.interception_record= irf
            attach.option = document_type
            attach.attachment = file
            attach.attachment_number = next_number
            attach.save()
        
        return Response ('')
            
    
    def create_pvf(self, request, request_json):
        form_number = request_json['formNumber']
        border_station = BorderStation.objects.get(station_code=form_number[0:3])
        
        pvf = VdfCommon()
        pvf.vdf_number = form_number
        pvf.station = border_station
        pvf.status = 'in-progress'
        pvf.victim = None
        pvf.save()
        
        next_number = 0
        pdfs = request_json['pdfs']
        for pdf in pdfs:
            document_type = pdf['documentType']
            file = pdf['file']
            self.add_file(request, file, 'vdf_attachments/')
            next_number += 1
            
            attach = VdfAttachmentCommon()
            attach.vdf = vdf
            attach.option = document_type
            attach.attachment = file
            attach.attachment_number = next_number
            attach.save()
        
        return Response ('')
    
    def create_sf(self, request, request_json):
        form_number = request_json['formNumber']
        border_station = BorderStation.objects.get(station_code=form_number[0:3])
        incident_number = self.incident_from_form_number(form_number)
        incident = Incident.objects.get(incident_number=incident_number)
        
        sf = Suspect()
        sf.sf_number = form_number
        sf.incidents.add(incident)
        sf.station = border_station
        sf.status = 'in-progress'
        sf.merged_person = None
        sf.save()
        
        next_number = 0
        pdfs = request_json['pdfs']
        for pdf in pdfs:
            document_type = pdf['documentType']
            file = pdf['file']
            self.add_file(request, file, 'sf_attachments/')
            next_number += 1
            
            attach = SuspectAttachment()
            attach.suspect = sf
            attach.option = document_type
            attach.attachment = file
            attach.attachment_number = next_number
            attach.save()
        
        return Response ('')
    
    def create_lf(self, request, request_json):
        form_number = request_json['formNumber']
        border_station = BorderStation.objects.get(station_code=form_number[0:3])
        incident_number = self.incident_from_form_number(form_number)
        incident = Incident.objects.get(incident_number=incident_number)
        
        lf = LocationForm()
        lf.incident = incident
        lf.lf_number = form_number
        lf.station = border_station
        lf.status = 'in-progress'
        lf.merged_place = ''
        lf.save()
        
        next_number = 0
        pdfs = request_json['pdfs']
        for pdf in pdfs:
            document_type = pdf['documentType']
            file = pdf['file']
            self.add_file(request, file, 'lf_attachments/')
            next_number += 1
            
            attach = LocationAttachment()
            attach.suspect = lf
            attach.option = document_type
            attach.attachment = file
            attach.attachment_number = next_number
            attach.save()
        
        return Response ('')
        