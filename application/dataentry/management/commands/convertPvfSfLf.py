import copy
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType

from dataentry.models import BorderStation, CifCommon, Form, Incident, PersonIdentification, VdfCommon, VdfAttachmentCommon, PersonForm
from dataentry.models import Suspect, SuspectInformation, SuspectAssociation, SuspectAttachment, SuspectEvaluation, SuspectLegal
from dataentry.models import LocationForm, LocationInformation, LocationAssociation, LocationAttachment, LocationEvaluation

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('CountryName', nargs='+', type=str)
        
    def handle(self, *args, **options):
        country_name = options.get('CountryName')[0]
        
        # Check that forms have not already been converted for this country
        stations = BorderStation.objects.filter(operating_country__name=country_name)
        stations_with_forms = []
        for station in stations:
            forms = station.form_set.filter(form_type__name__in=['PVF','SF','LF'])
            if len(forms) > 0:
                stations_with_forms.append(station)
        
        if len(stations_with_forms) > 0:
            print ('The following stations already have new forms')
            for station in stations_with_forms:
                print(station.station_name)
                return
        
        new_forms = {}
        for form_type in ['pvf','sf','lf']:
            form = Form.objects.get(form_name=form_type + country_name)
            new_forms[form_type] = form
        
        cif_type = ContentType.objects.get(app_label='dataentry', model='cifcommon')
            
        with transaction.atomic():
            pvfs = VdfCommon.objects.filter(station__operating_country__name=country_name)
            for pvf in pvfs:
                incident = self.get_incident_from_form(pvf)   
            
            cif_count = 0
            print('Populating from CIFs')
            cifs = CifCommon.objects.filter(station__operating_country__name=country_name)
            for cif in cifs:
                incident = self.get_incident_from_form(cif)
                cif_count += 1
                if cif_count % 1000 == 0:
                    print(cif_count)
                
                pvfs = VdfCommon.objects.filter(station=incident.station, vdf_number__startswith=incident.incident_number)
                for pvf in pvfs:
                    if len(pvf.vdf_number) > len(incident.incident_number):
                        next_char = pvf.vdf_number[len(incident.incident_number)]
                        if next_char >= '0' and next_char <= '9':
                            continue
                    
                    if pvf.victim.master_person != cif.main_pv.master_person and pvf.victim.full_name != cif.main_pv.full_name:
                        continue
                    
                    self.populate_pvf_from_cif(pvf, cif)
                
                for pb in cif.personboxcommon_set.all():
                    if pb.person.role != 'witness':
                        sfs = Suspect.objects.filter(sf_number__startswith=incident.incident_number, merged_person__master_person=pb.person.master_person)
                        if len(sfs) < 1:
                            sfs = Suspect.objects.filter(sf_number__startswith=incident.incident_number, merged_person__full_name=pb.person.full_name)
                        if len(sfs) < 1:
                            self.create_suspect_form(pb, cif, incident)
                        else:
                            self.update_suspect_form(sfs[0], pb, cif, incident)
                
                lfs = LocationForm.objects.filter(lf_number__startswith=incident.incident_number)
                for lb in cif.locationboxcommon_set.all():
                    found = False
                    for lf in lfs:
                        if self.match_location(lf, lb):
                            self.update_lf(lf, lb, cif, incident)
                            found = True
                            break
                    
                    if not found:
                        self.create_lf(lb, cif, incident)
                
                # Remove PersonForm entries that linked to CIF
                person_forms = PersonForm.objects.filter(content_type=cif_type, object_id=cif.id)
                for person_form in person_forms:
                    person_form.delete()
            
            for station in stations:
                vdf_forms = station.form_set.filter(form_type__name = 'VDF')
                if len(vdf_forms) == 1:
                    station.form_set.remove(vdf_forms[0])
                    station.form_set.add(new_forms['pvf'])
                    station.save()
                
                cif_forms = station.form_set.filter(form_type__name = 'CIF')
                if len(cif_forms) == 1:
                    station.form_set.remove(cif_forms[0])
                    station.form_set.add(new_forms['sf'])
                    station.form_set.add(new_forms['lf'])
                    station.save()
                        
    def get_incident_from_form(self, form_object):
        form_number = form_object.get_key()
        incident_number = form_number
        for idx in range(3,len(form_number)):
            if form_number[idx] < '0' or form_number[idx] > '9':
                incident_number = form_number[0:idx]
                break
        
        try:
            incident = Incident.objects.get(incident_number=incident_number)
        except ObjectDoesNotExist:
            incident = Incident()
            incident.incident_number = incident_number
            incident.station = form_object.station
            incident_date = form_object.get_form_date()
            if incident_date is None:
                incident_date = datetime.now()
            incident.incident_date = incident_date
            incident.save()
            
        return incident
    
    def populate_pvf_from_cif(self, pvf, cif):  
        pvf.pv_recruited_agency = cif.recruited_agency
        pvf.pv_recruited_broker = cif.recruited_broker
        pvf.pv_recruited_no = cif.recruited_no
        pvf.recruited_agency_name = self.pb_instance_name(cif, cif.recruited_agency_pb)
        pvf.recruited_broker_names = self.pb_instance_name(cif, cif.recruited_broker_pb)
        
        recruited_options = [
            {'field':'how_recruited_promised_job','value':'Promised a job'},
            {'field':'how_recruited_married','value':'Married'},
            {'field':'how_recruited_promised_marriage','value':'Promised marriage'},
            {'field':'how_recruited_at_work','value':'Approached at work'},
            {'field':'how_recruited_at_school','value':'Approached at school'},
            {'field':'how_recruited_job_ad','value':'Online job advertisement'},
            {'field':'how_recruited_broker_online','value':'Met suspect online'},
            {'field':'how_recruited_broker_approached','value':'suspect approached directly'},
            {'field':'how_recruited_broker_through_friends','value':'Through friends'},
            {'field':'how_recruited_broker_through_family','value':'Through family'},
            {'field':'how_recruited_broker_called_pv','value':"Suspect called PV's mobile"}
            ]
        pvf.pv_recruited_how = None
        for option in recruited_options:
            recruited_flag = getattr(cif, option['field'])
            if recruited_flag:
                if pvf.pv_recruited_how is not None and len(pvf.pv_recruited_how) > 0:
                    pvf.pv_recruited_how += ';' + option['value']
                else:
                    pvf.pv_recruited_how = option['value']
        
        if cif.how_recruited_broker_other is not None and cif.how_recruited_broker_other != '':
            if pvf.pv_recruited_how is not None and len(pvf.pv_recruited_how) > 0:
                pvf.pv_recruited_how += ';' + cif.how_recruited_broker_other
            else:
                pvf.pv_recruited_how = cif.how_recruited_broker_other
        
        
        expense_options = [
            {'field':'travel_expenses_paid_to_broker','value':'The PV paid to broker'},
            {'field':'travel_expenses_paid_themselves','value':'The PV paid themselves'},
            {'field':'travel_expenses_paid_by_broker','value':'Suspect paid all expenses'},
            {'field':'travel_expenses_paid_by_broker_repaid','value':'Suspect paid which must be repaid'},
            ]
        pvf.pv_expenses_paid_how = None
        for option in expense_options:
            expense_flag = getattr(cif, option['field'])
            if expense_flag:
                if pvf.pv_expenses_paid_how is not None and pvf.pv_expenses_paid_how != '':
                    pvf.pv_expenses_paid_how += ';' + option['value']
                else:
                    pvf.pv_expenses_paid_how = option['value']
        pvf.pv_paid_broker_amount = cif.travel_expenses_paid_to_broker_amount
        pvf.broker_paid_amount = cif.travel_expenses_broker_repaid_amount
        
        pvf.job_promised_amount = cif.expected_earning
        
        pvf.pv_traveled_how = None
        for travel in cif.transportationcommon_set.all():
            if (travel.transportation_kind is not None and travel.transportation_kind != '' and
                    (pvf.pv_traveled_how is None or travel.transportation_kind not in pvf.pv_traveled_how)):
                if pvf.pv_traveled_how is not None and pvf.pv_traveled_how != '':
                    pvf.pv_traveled_how += ';' + travel.transportation_kind
                else:
                    pvf.pv_traveled_how = travel.transportation_kind
        
        if cif.exploitation_forced_prostitution_occ:
            pvf.exploit_prostitution = cif.exploitation_forced_prostitution_occ
            pvf.exploit_prostitution_suspects = self.pb_instance_name(cif, cif.exploitation_forced_prostitution_pb)
        if cif.exploitation_sexual_abuse_occ:
            pvf.exploit_sexual_abuse = cif.exploitation_sexual_abuse_occ
            pvf.exploit_sexual_abuse_suspects = self.pb_instance_name(cif, cif.exploitation_sexual_abuse_pb)
        if cif.exploitation_physical_abuse_occ:
            pvf.exploit_physical_abuse = cif.exploitation_physical_abuse_occ
            pvf.exploit_physical_abuse_suspects = self.pb_instance_name(cif, cif.exploitation_physical_abuse_pb)
        if cif.exploitation_debt_bondage_occ:
            pvf.exploit_debt_bondage = cif.exploitation_debt_bondage_occ
            pvf.exploit_debt_bondage_suspects = self.pb_instance_name(cif, cif.exploitation_debt_bondage_pb)
        if cif.exploitation_forced_labor_occ:
            pvf.exploit_forced_labor = cif.exploitation_forced_labor_occ
            pvf.exploit_forced_labor_suspects = self.pb_instance_name(cif, cif.exploitation_forced_labor_pb)
        if cif.exploitation_organ_removal_occ:
            pvf.exploit_other = 'Organ Removal'
            if cif.exploitation_organ_removal_pb is not None and cif.exploitation_organ_removal_pb != '':
                pvf.exploit_other_suspects = self.pb_instance_name(cif, cif.exploitation_organ_removal_pb)
        if cif.exploitation_other_occ:
            pvf.exploit_other = cif.exploitation_other_value
            if cif.exploitation_other_pb is not None and cif.exploitation_other_pb != '':
                pvf.exploit_other_suspects = self.pb_instance_name(cif, cif.exploitation_other_pb)
        
        pvf.save()
        
        attachment_number = 0
        for attachment in pvf.vdfattachmentcommon_set.all():
            if attachment.attachment_number > attachment_number:
                attachment_number = attachment.attachment_number
        
        for attachment in cif.cifattachmentcommon_set.all():
            attachment_number += 1
            new_attachment = VdfAttachmentCommon()
            new_attachment.vdf = pvf
            new_attachment.attachment_number = attachment_number
            new_attachment.description = attachment.description
            new_attachment.attachment = attachment.attachment
            new_attachment.private_card = attachment.private_card
            new_attachment.option = attachment.option
            new_attachment.save()
            
            
    def pb_instance_name (self, cif, pb):
        value = None
        if pb is not None:
            pb_numbers = pb.split(',')
            pbs = cif.personboxcommon_set.all()
            for pb_item in pb_numbers:
                try:
                    pb_number = int(pb_item)
                except:
                    continue
                
                for pb_entry in pbs:
                    #print('pb_instance_name', cif.cif_number, pb_number, pb_entry.pb_number)
                    if pb_number == pb_entry.pb_number:
                        #print('pb_instance_name match===', cif.cif_number, pb_number, pb_entry.pb_number)
                        tmp = pb_entry.person.full_name
                        if value is None:
                            value = tmp
                        else:
                            value = ';' + tmp
                        break
             
        return value
    
    def checkbox_append(self, current, value):
        if current is None or current == '':
            result = value
        else:
            result = current + ';' + value
        return result
    
    def update_suspect_attachment(self, cif, suspect):
        attachment_number = 0
        for attachment in suspect.suspectattachment_set.all():
            if attachment.attachment_number > attachment_number:
                attachment_number = attachment.attachment_number
        
        for attachment in cif.cifattachmentcommon_set.all():
            attachment_number += 1
            new_attachment = SuspectAttachment()
            new_attachment.suspect = suspect
            new_attachment.attachment_number = attachment_number
            new_attachment.description = attachment.description
            new_attachment.attachment = attachment.attachment
            new_attachment.private_card = attachment.private_card
            new_attachment.option = attachment.option
            new_attachment.save()
    
    def create_suspect_form(self, pb, cif, incident):
        info_person = copy.deepcopy(pb.person)
        merged_person = copy.deepcopy(pb.person)
        info_person.id = merged_person.id = None
        info_person.save()
        merged_person.save()
        
        next_suffix = 'A'
        existing_suspects = Suspect.objects.filter(incidents=incident)
        for existing_suspect in existing_suspects:
            suffix = existing_suspect.sf_number[len(incident.incident_number)]
            if suffix >= next_suffix:
                next_suffix = chr(ord(suffix) + 1)

        suspect = Suspect()
        suspect.station = cif.station
        suspect.status = 'approved'
        suspect.sf_number = incident.incident_number + next_suffix
        suspect.merged_person = merged_person
        suspect.save()
        
        suspect.incidents.add(incident)
        suspect.save()
        
        ids = PersonIdentification.objects.filter(person=pb.person)
        for id in ids:
            info_id = copy.deepcopy(id)
            merged_id = copy.deepcopy(id)
            info_id.id = merged_id.id = None
            info_id.person = info_person
            info_id.save()
            merged_id.person = merged_person
            merged_id.save()
        
        info = SuspectInformation()
        info.suspect = suspect
        info.incident = incident
        info.source_type = cif.source_of_intelligence
        if info.source_type == 'Informant #' and cif.main_pv.full_name == '':
            info.source_title = ''
        else:
            info.source_title = cif.main_pv.full_name
        info.interviewer_name = cif.staff_name if cif.staff_name is not None else ''
        info.interview_date = cif.interview_date
        info.location = cif.location if cif.location is not None else ''
        info.person = info_person
        info.save()
        
        assoc = SuspectAssociation()
        assoc.suspect = suspect
        assoc.incident = incident
        assoc.save()
        
        legal = SuspectLegal()
        legal.suspect = suspect
        legal.incident = incident
        legal.pv_unable = ''
        if cif.legal_action_taken_staff_pv_afraid_reputation:
            legal.pv_unable = self.checkbox_append(legal.pv_unable, 'PV afraid for reputation')
        if cif.legal_action_taken_staff_pv_afraid_safety:
            legal.pv_unable = self.checkbox_append(legal.pv_unable, 'PV afraid for their safety')
        if cif.legal_action_taken_staff_pv_does_not_believe:
            legal.pv_unable = self.checkbox_append(legal.pv_unable, "PVs don't believe they were being trafficked")
        if cif.legal_action_taken_staff_family_not_willing:
            legal.pv_unable = self.checkbox_append(legal.pv_unable, "PV family not willing")
        legal.location_unable = ''
        if cif.legal_action_taken_staff_trafficker_ran or cif.trafficker_ran_away:
            legal.location_unable = self.checkbox_append(legal.location_unable, "trafficker_ran_away")
        legal.police_unable = ''
        if cif.police_say_not_enough_evidence:
            legal.police_unable = self.checkbox_append(legal.police_unable, "Police say not enough evidence")
        if cif.police_do_not_believe_crime:
            legal.police_unable = self.checkbox_append(legal.police_unable, "Police do not believe it is a crime")
        legal.save()
        if pb.person.interviewer_believes is not None and pb.person.interviewer_believes != '':
            eval = SuspectEvaluation()
            eval.suspect = suspect
            eval.incident = incident
            eval.evaluator_type = 'Interviewer'
            eval.evaluator_name = cif.staff_name
            eval.evaluation = pb.person.interviewer_believes
            eval.save()
        if pb.person.pv_believes is not None and pb.person.pv_believes != '':
            eval = SuspectEvaluation()
            eval.suspect = suspect
            eval.incident = incident
            eval.evaluator_type = 'PV'
            eval.evaluator_name = cif.main_pv.full_name
            eval.evaluation = pb.person.pv_believes
            eval.save()
        
        self.update_suspect_attachment(cif, suspect)
    
    def update_suspect_form(self, suspect_form, pb, cif, incident):
        info_person = copy.deepcopy(pb.person)
        info_person.id = None
        info_person.save()
        
        info = SuspectInformation()
        info.suspect = suspect_form
        info.incident = incident
        info.source_type = cif.source_of_intelligence
        if info.source_type == 'Informant #' and cif.main_pv.full_name == '':
            info.source_title = ''
        else:
            info.source_title = cif.main_pv.full_name
        info.interviewer_name = cif.staff_name if cif.staff_name is not None else ''
        info.interview_date = cif.interview_date
        info.location = cif.location if cif.location is not None else ''
        info.person = info_person
        info.save()
        
        for field in ['full_name','gender','age','address','latitude','longitude','address_notes',
                      'phone_contact','birthdate','estimated_birthdate','nationality','photo',
                      'social_media','social_media_platform','role','appearance','occupation']:
            tmp = getattr(info_person, field, None)
            if tmp is not None and tmp != '':
                mrg = getattr(suspect_form.merged_person, field, None)
                if mrg is None or tmp == '':
                    setattr(suspect_form.merged_person, field, tmp)
        
        suspect_form.merged_person.save()
        
        ids = PersonIdentification.objects.filter(person=pb.person)
        for id in ids:
            try:
                merged_id = PersonIdentification.objects.get(person=suspect_form.merged_person, type=id.type)
            except ObjectDoesNotExist:
                merged_id = copy.deepcopy(id)
                merged_id.id = None
                merged_id.person = suspect_form.merged_person
                merged_id.save()
        
        legal = SuspectLegal.objects.get(suspect=suspect_form)
        if cif.legal_action_taken_staff_pv_afraid_reputation and 'PV afraid for reputation' not in legal.pv_unable:
            legal.pv_unable = self.checkbox_append(legal.pv_unable, 'PV afraid for reputation')
        if cif.legal_action_taken_staff_pv_afraid_safety and 'PV afraid for their safety' not in legal.pv_unable:
            legal.pv_unable = self.checkbox_append(legal.pv_unable, 'PV afraid for their safety')
        if cif.legal_action_taken_staff_pv_does_not_believe and "PVs don't believe they were being trafficked" not in legal.pv_unable:
            legal.pv_unable = self.checkbox_append(legal.pv_unable, "PVs don't believe they were being trafficked")
        if cif.legal_action_taken_staff_family_not_willing and "PV family not willing" not in legal.pv_unable:
            legal.pv_unable = self.checkbox_append(legal.pv_unable, "PV family not willing")
        
        if (cif.legal_action_taken_staff_trafficker_ran or cif.trafficker_ran_away) and "trafficker_ran_away" not in legal.location_unable:
            legal.location_unable = self.checkbox_append(legal.location_unable, "trafficker_ran_away")
        
        if cif.police_say_not_enough_evidence and "Police say not enough evidence" not in legal.police_unable:
            legal.police_unable = self.checkbox_append(legal.police_unable, "Police say not enough evidence")
        if cif.police_do_not_believe_crime and "Police do not believe it is a crime" not in legal.police_unable:
            legal.police_unable = self.checkbox_append(legal.police_unable, "Police do not believe it is a crime")
        legal.save()
        
        if pb.person.interviewer_believes is not None and pb.person.interviewer_believes != '':
            try:
                eval = SuspectEvaluation.objects.get(suspect=suspect_form, evaluator_name=cif.staff_name)
            except ObjectDoesNotExist:
                eval = SuspectEvaluation()
                eval.suspect = suspect_form
                eval.incident = incident
                eval.evaluator_type = 'Interviewer'
                eval.evaluator_name = cif.staff_name
                eval.evaluation = pb.person.interviewer_believes
                eval.save()
            
        if pb.person.pv_believes is not None and pb.person.pv_believes != '':
            eval = SuspectEvaluation()
            eval.suspect = suspect_form
            eval.incident = incident
            eval.evaluator_type = 'PV'
            eval.evaluator_name = cif.main_pv.full_name
            eval.evaluation = pb.person.pv_believes
            eval.save()
        
        self.update_suspect_attachment(cif, suspect_form)
        
    def match_location(self, lf, lb):
        result = False
        if lf.merged_address is not None and 'address' in lf.merged_address and lb.address is not None and 'address' in lb.address:
            result = (lf.merged_address['address'] == lb.address['address'] and lf.merged_place == lb.place and 
                      lf.merged_place_kind == lb.place_kind and lf.merged_description == lb.address_notes)
        
        return result
        
    def create_lf(self, lb, cif, incident):
        lf = LocationForm()
        
        next_suffix = 'A'
        existing_suspects = LocationForm.objects.filter(incidents=incident)
        for existing_suspect in existing_suspects:
            suffix = existing_suspect.lf_number[len(incident.incident_number)]
            if suffix >= next_suffix:
                next_suffix = chr(ord(suffix) + 1)
        
        lf.lf_number = incident.incident_number + next_suffix
        lf.station = cif.station
        lf.status = 'approved'
        lf.save()
        lf.incidents.add(incident)
        lf.save()
        
        self.update_lf(lf, lb, cif, incident)
    
    def update_lf(self, lf, lb, cif, incident):
        info = LocationInformation()
        info.lf =lf
        info.incident = incident
        info.source_type = cif.source_of_intelligence
        if info.source_type == 'Informant #' and cif.main_pv.full_name == '':
            info.source_title = ''
        else:
            info.source_title = cif.main_pv.full_name
        info.interviewer_name = cif.staff_name if cif.staff_name is not None else ''
        info.interview_date = cif.interview_date
        info.location = cif.location if cif.location is not None else ''
        info.place = lb.place
        info.place_kind = lb.place_kind
        info.address = lb.address
        info.latitude = lb.latitude
        info.longitude = lb.longitude
        info.phone = lb.phone
        info.name_signboard = lb.name_signboard
        info.location_in_town = lb.location_in_town
        info.color = lb.color
        info.number_of_levels = lb.number_of_levels
        info.description = lb.address_notes
        info.nearby_landmarks = lb.nearby_landmarks
        
        info.save()
        
        infos = LocationInformation.objects.filter(lf=lf)
        for field in ['place','place_kind','address','latitude','longitude','phone',
                      'name_signboard','location_in_town','color','number_of_levels',
                      'description','nearby_landmarks']:
            current_merged = getattr(lf, 'merged_' + field, None)
            for info in infos:
                if current_merged is None or current_merged == '':
                    tmp = getattr(info, field, None)
                    if tmp is not None and tmp != '':
                        setattr(lf, 'merged_' + field, tmp)
                        break
        lf.save()
        
        assoc = LocationAssociation()
        assoc.lf =lf
        assoc.incident = incident
        assoc.source_type = cif.source_of_intelligence
        if assoc.source_type == 'Informant #' and cif.main_pv.full_name == '':
            assoc.source_title = ''
        else:
            assoc.source_title = cif.main_pv.full_name
        assoc.interviewer_name = cif.staff_name if cif.staff_name is not None else ''
        assoc.interview_date = cif.interview_date
        assoc.location = cif.location if cif.location is not None else ''
        assoc.person_in_charge = lb.person_in_charge
        assoc.pvs_visited = cif.main_pv.full_name
        if lb.pv_stayed_days is not None and lb.pv_stayed_days != '':
            assoc.stay_how_long = lb.pv_stayed_days
            assoc.start_date = lb.pv_stayed_start_date
        elif lb.pv_stayed_not_applicable:
            assoc.stay_how_long = 'N/A (Not Applicable)'
        if lb.pv_attempt_hide_yes:
            assoc.attempt_hide = 'Yes'
            assoc.attempt_explanation = lb.pv_attempt_hide_explaination
        elif lb.pv_attempt_hide_no:
            assoc.attempt_hide = 'No'
        if lb.pv_free_to_go_no:
            assoc.free_to_go = 'No'
            assoc.free_to_go_explanation = lb.pv_free_to_go_explaination
        elif lb.pv_free_to_go_yes:
             assoc.free_to_go = 'Yes'
        assoc.suspects_associative = self.pb_instance_name(cif, lb.associated_pb)
        assoc.save()
        
        attachment_number = 0
        for attachment in lf.locationattachment_set.all():
            if attachment.attachment_number > attachment_number:
                attachment_number = attachment.attachment_number
        
        for attachment in cif.cifattachmentcommon_set.all():
            attachment_number += 1
            new_attachment = LocationAttachment()
            new_attachment.lf = lf
            new_attachment.attachment_number = attachment_number
            new_attachment.description = attachment.description
            new_attachment.attachment = attachment.attachment
            new_attachment.private_card = attachment.private_card
            new_attachment.option = attachment.option
            new_attachment.save()
        
                
             
        