import datetime
import math
import re
import json

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from dataentry.models import Audit, AuditSample, BorderStation, Country, Form, FormCategory, Incident
from dataentry.models import Gospel, GospelVerification, IndicatorHistory, IntercepteeCommon, IrfCommon, LocationInformation
from dataentry.models import SiteSettings, SuspectInformation


class CollectionResults:
    def __init__(self, label):
        self.label = label
        
        self.irf_count = 0
        self.victim_count = 0
        self.victim_present_count = 0
        self.suspect_count = 0
        self.suspect_present_count = 0
        self.victim_evidence_count = 0
        self.photo_count = 0
        self.suspect_photo_count = 0
        self.phone_count = 0
        self.phone_verified_count = 0
        self.irf_compliance_count = 0
        self.irf_lag_total = 0
        self.irf_lag_percent_total = 0
        self.irf_lag_count = 0
        self.irf_forms_verified = 0
        self.evidence_count = 0
        self.invalid_intercept_count = 0
        self.high_risk_count = 0
        
        self.cif_count = 0
        self.cif_compliance_count = 0
        self.cif_lag_total = 0
        self.cif_lag_percent_total = 0
        self.cif_lag_count = 0
        self.cif_with_evidence_count = 0
        
        self.vdf_count = 0
        self.vdf_compliance_count = 0
        self.vdf_lag_total = 0
        self.vdf_lag_percent_total = 0
        self.vdf_lag_count = 0
        self.vdf_gospel_count = 0
        self.gospel_profession_count = 0
        self.profession_denominator = 0
        self.gsp_count = 0
        self.gospel_verification_count = 0
        self.gospel_lag_total = 0
        self.gospel_lag_count = 0
        self.gospel_lag_percent_total = 0
        
        self.sf_count = 0
        self.sf_compliance_count = 0
        self.sf_lag_total = 0
        self.sf_lag_percent_total = 0
        self.sf_lag_count = 0
        
        self.lf_count = 0
        self.lf_compliance_count = 0
        self.lf_lag_total = 0
        self.lf_lag_percent_total = 0
        self.lf_lag_count = 0
    
    def compute_percent(self, numerator, denominator):
        if denominator < 1:
            return ''
        else:
            return math.floor(numerator * 100 / denominator + 0.5)
    
    def score_lag(self, lag_time):
        score = 0
        if lag_time <= 1:
            score = 100
        elif lag_time <= 2:
            score = 90
        elif lag_time <= 3:
            score = 80
        elif lag_time <= 7:
            score = 60
        elif lag_time <= 30:
            score = 30
        
        return score
        
    def compute_values(self, pvf_form):
        self.irf_compliance_percent = self.compute_percent(self.irf_compliance_count, self.irf_count)
        
        self.cif_percent = self.compute_percent(self.cif_count, self.victim_count)
        self.cif_compliance_percent = self.compute_percent(self.cif_compliance_count, self.cif_count)
        
        self.vdf_compliance_percent = self.compute_percent(self.vdf_compliance_count, self.vdf_count)
        self.vdf_gospel_percent = self.compute_percent(self.vdf_gospel_count, self.vdf_count)
        self.gospel_profession_percent = self.compute_percent(self.gospel_profession_count, self.profession_denominator)
        
        self.sf_percent = self.compute_percent(self.sf_count, self.suspect_count)
        self.sf_compliance_percent = self.compute_percent(self.sf_compliance_count, self.sf_count)
        
        self.lf_compliance_percent = self.compute_percent(self.lf_compliance_count, self.lf_count)
        
        self.verified_forms = self.evidence_count + self.invalid_intercept_count + self.high_risk_count
        self.evidence_percent = self.compute_percent(self.evidence_count, self.verified_forms)
        self.invalid_intercept_percent = self.compute_percent(self.invalid_intercept_count, self.verified_forms)
        self.high_risk_percent = self.compute_percent(self.high_risk_count, self.verified_forms)
        
        self.vdf_percent = self.compute_percent(self.vdf_count, self.victim_count)
        self.photo_percent = self.compute_percent(self.photo_count, self.victim_present_count)
        self.suspect_photo_percent = self.compute_percent(self.suspect_photo_count, self.suspect_present_count)
        self.phone_verified_percent = self.compute_percent(self.phone_verified_count, self.phone_count)
        if pvf_form:
            self.compliance_percent = self.compute_percent(self.irf_compliance_count + self.sf_compliance_count + self.lf_compliance_count + self.vdf_compliance_count,
                                self.irf_count + self.sf_count + self.lf_count + self.vdf_count)
        else:
            self.compliance_percent = self.compute_percent(self.irf_compliance_count +self.cif_compliance_count + self.vdf_compliance_count,
                                self.irf_count + self.cif_count + self.vdf_count)
        
        lag_count_numerator = 0
        lag_count_denominator = 0
        if self.irf_lag_count > 0:
            self.irf_lag = math.floor(self.irf_lag_total / self.irf_lag_count + 0.5)
            self.irf_lag_score = math.floor(self.irf_lag_percent_total/self.irf_lag_count + 0.5)
            lag_count_denominator += 1
            lag_count_numerator += self.irf_lag_score
        else:
            self.irf_lag = 0
        if self.cif_lag_count > 0:
            self.cif_lag = math.floor(self.cif_lag_total / self.cif_lag_count + 0.5)
            self.cif_lag_score = math.floor(self.cif_lag_percent_total/self.cif_lag_count + 0.5)
            lag_count_denominator += 1
            lag_count_numerator += self.cif_lag_score
        else:
            self.cif_lag = 0
        if self.vdf_lag_count > 0:
            self.vdf_lag = math.floor(self.vdf_lag_total / self.vdf_lag_count + 0.5)
            self.vdf_lag_score = math.floor(self.vdf_lag_percent_total/self.vdf_lag_count + 0.5)
            lag_count_denominator += 1
            lag_count_numerator += self.vdf_lag_score
        else:
            self.vdf_lag = 0
        if self.gospel_lag_count > 0:
            self.gospel_lag = math.floor(self.gospel_lag_total / self.gospel_lag_count + 0.5)
            self.gospel_lag_score = math.floor(self.gospel_lag_percent_total/self.gospel_lag_count + 0.5)
        else:
            self.gospel_lag = 0
        if self.sf_lag_count > 0:
            self.sf_lag = math.floor(self.sf_lag_total / self.sf_lag_count + 0.5)
            self.sf_lag_score = math.floor(self.sf_lag_percent_total/self.sf_lag_count + 0.5)
            lag_count_denominator += 1
            lag_count_numerator += self.sf_lag_score
        else:
            self.sf_lag = 0
        if self.lf_lag_count > 0:
            self.lf_lag = math.floor(self.lf_lag_total / self.lf_lag_count + 0.5)
            self.lf_lag_score = math.floor(self.lf_lag_percent_total/self.lf_lag_count + 0.5)
            lag_count_denominator += 1
            lag_count_numerator += self.lf_lag_score
        else:
            self.lf_lag = 0
        
        if lag_count_denominator > 0:
            self.collection_lag_time = math.floor(lag_count_numerator / lag_count_denominator + 0.5)
        else:
            self.collection_lag_time = ''
                
        self.evidence_cif_percent = self.compute_percent(self.cif_with_evidence_count, self.victim_evidence_count)
        self.valid_intercept_percent = self.compute_percent(self.evidence_count + self.high_risk_count,
                            self.evidence_count + self.high_risk_count + self.invalid_intercept_count)
        
        metric_present = 0
        metric_total = 0
        if pvf_form:
            if self.vdf_percent != '':
                metric_present += 0.20
                metric_total += self.vdf_percent * 0.20
            if self.sf_percent != '':
                metric_present += 0.20
                metric_total += self.sf_percent * 0.20
            if self.photo_percent != '':
                metric_present += 0.075
                metric_total += self.photo_percent * 0.075
            if self.phone_verified_percent != '':
                metric_present += 0.075
                metric_total += self.phone_verified_percent * 0.075
        else:
            if self.vdf_percent != '':
                metric_present += 0.15
                metric_total += self.vdf_percent * 0.15
            if self.evidence_cif_percent != '':
                metric_present += 0.15
                metric_total += self.evidence_cif_percent * 0.15
            if self.photo_percent != '':
                metric_present += 0.1
                metric_total += self.photo_percent * 0.1
            if self.phone_verified_percent != '':
                metric_present += 0.1
                metric_total += self.phone_verified_percent * 0.1
        if self.compliance_percent != '':
            metric_present += 0.2
            metric_total += self.compliance_percent * 0.2
        if self.collection_lag_time != '':
            metric_present += 0.15
            metric_total += self.collection_lag_time * 0.15
        if self.valid_intercept_percent != '':
            metric_present += 0.1
            metric_total += self.valid_intercept_percent * 0.1
        if metric_present > 0:
            self.compliance_total = math.floor(metric_total/metric_present + 0.5)
        else:
            self.compliance_total = ''
        
    
    def sum_list(self, the_list):
        for entry in the_list:
            self.irf_count += entry.irf_count
            self.victim_count += entry.victim_count
            self.victim_present_count += entry.victim_present_count
            self.suspect_count += entry.suspect_count
            self.suspect_present_count += entry.suspect_present_count
            self.victim_evidence_count += entry.victim_evidence_count
            self.photo_count += entry.photo_count
            self.suspect_photo_count += entry.suspect_photo_count
            self.phone_count += entry.phone_count
            self.phone_verified_count += entry.phone_verified_count
            self.irf_compliance_count += entry.irf_compliance_count
            self.irf_lag_total += entry.irf_lag_total
            self.irf_lag_percent_total += entry.irf_lag_percent_total
            self.irf_lag_count += entry.irf_lag_count
            self.irf_forms_verified += entry.irf_forms_verified
            self.evidence_count += entry.evidence_count
            self.invalid_intercept_count += entry.invalid_intercept_count
            self.high_risk_count += entry.high_risk_count
            
            self.cif_count += entry.cif_count
            self.cif_compliance_count += entry.cif_compliance_count
            self.cif_lag_total += entry.cif_lag_total
            self.cif_lag_percent_total += entry.cif_lag_percent_total
            self.cif_lag_count += entry.cif_lag_count
            self.cif_with_evidence_count += entry.cif_with_evidence_count
            
            self.vdf_count += entry.vdf_count
            self.vdf_compliance_count += entry.vdf_compliance_count
            self.vdf_lag_total += entry.vdf_lag_total
            self.vdf_lag_percent_total += entry.vdf_lag_percent_total
            self.vdf_lag_count += entry.vdf_lag_count
            self.vdf_gospel_count += entry.vdf_gospel_count
            self.gospel_lag_total += entry.gospel_lag_total
            self.gospel_lag_percent_total += entry.gospel_lag_percent_total
            self.gospel_lag_count += entry.gospel_lag_count
            self.gospel_profession_count += entry.gospel_profession_count
            self.gospel_verification_count += entry.gospel_verification_count
            self.profession_denominator += entry.profession_denominator
            self.gsp_count += entry.gsp_count
            
            self.sf_count += entry.sf_count
            self.sf_compliance_count += entry.sf_compliance_count
            self.sf_lag_total += entry.sf_lag_total
            self.sf_lag_percent_total += entry.sf_lag_percent_total
            self.sf_lag_count += entry.sf_lag_count
            
            self.lf_count += entry.lf_count
            self.lf_compliance_count += entry.lf_compliance_count
            self.lf_lag_total += entry.lf_lag_total
            self.lf_lag_percent_total += entry.lf_lag_percent_total
            self.lf_lag_count += entry.lf_lag_count

class IndicatorsViewSet(viewsets.ViewSet):
    def calculate_indicators(self, request, country_id):
        end_date = datetime.datetime.now().date()
        start_date = end_date - datetime.timedelta(30)
        results = {}
        months = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        
        
        country = Country.objects.get(id=country_id)
        if country.verification_goals is None:
            goals = {
                    'irfLag': 5,
                    'photosLag': 5,
                    'vdfLag': 5,
                    'pvfLag': 5,
                    'cifLag': 5,
                    'sfLag': 5,
                    'lfLag': 5,
                    'v1Lag': 4,
                    'v1Backlog': 10,
                    'v2Lag': 7,
                    'v2Backlog': 10,
                    }
        else:
            goals = country.verification_goals
            
        current_results = IndicatorHistory.calculate_indicators(start_date, end_date, country, include_latest_date=True)
        current_results['title1'] = 'Last 30'
        current_results['title2'] = 'Days'
        results['latest'] = current_results
        results['goals'] = goals
        
        history = []
        history_entries = IndicatorHistory.objects.filter(country=country).order_by("-year","-month")
        for history_entry in history_entries:
            results_entry = history_entry.indicators
            results_entry['title1']=months[history_entry.month]
            results_entry['title2']=str(history_entry.year)
            history.append(results_entry)
        
        results['history'] = history
        
        #Audits
        exclude_audits = AuditSample.objects.filter(completion_date__isnull=True).values_list('audit__id',flat=True)
        audit_results = {}
        for form_type in ['IRF','CIF','VDF', 'PVF', 'SF', 'LF']:
            audit = self.latest_audit(form_type, country_id, exclude_audits)
            if audit is None:
                audit_results[form_type] = {
                        'label': 'Last ' + form_type + ' Audit (none)',
                        'value': ''
                    }
            else:
                
                audit_results[form_type] = {
                        'label': 'Last ' + form_type + ' Audit (' + str(audit.start_date.month) + '/' + str(audit.start_date.year) + ' to ' + \
                                str(audit.end_date.month) + '/' + str(audit.end_date.year) + ')',
                        'value': audit.accuracy()
                    }
        results['audit'] = audit_results 
        results['blind'] = IrfCommon.has_blind_verification(country)
        
        return Response(results)
    
    def latest_audit(self, type_name, country_id, exclude_audits):
        audit = None
        form_names = Form.objects.filter(form_type__name=type_name).values_list('form_name', flat=True)
        audits = Audit.objects.filter(country__id=country_id, form_name__in=form_names).exclude(id__in=exclude_audits).order_by('-end_date')
        if len(audits) > 0:
            audit = audits[0]
        return audit
    
    def get_collection_indicators(self, request, country_id):
        start_date = request.GET['start_date']
        end_date = request.GET['end_date']
        
        return Response(IndicatorsViewSet.compute_collection_indicators(start_date, end_date, country_id))
    
    @staticmethod
    def score_lag(lag_time):
        score = 0
        if lag_time <= 1:
            score = 100
        elif lag_time <= 2:
            score = 90
        elif lag_time <= 3:
            score = 80
        elif lag_time <= 7:
            score = 60
        elif lag_time <= 30:
            score = 30
        
        return score
    
    @staticmethod
    def compute_collection_indicators(start_date, end_date, country_id):
        results = []
        station_list = BorderStation.objects.filter(operating_country__id=country_id, features__contains='hasForms').order_by('station_code')
        pvf_form = False
        for station in station_list:
            form = Form.current_form('IRF', station.id)
            if form is None:
                continue
            
            the_pvf_form = Form.current_form('PVF', station.id)
            if the_pvf_form is not None:
                pvf_form = True
            
            form_categories = FormCategory.objects.filter(form=form, name='People')
            if len(form_categories) == 1 and form_categories[0].storage is not None:
                interceptee_storage = form_categories[0].storage
            else:
                interceptee_storage = None
                continue
            
            result = CollectionResults(station.station_code)
            irf_class = form.storage.get_form_storage_class()
            irfs = irf_class.objects.filter(station=station, verified_date__gte=start_date, verified_date__lte=end_date)
            for irf in irfs:
                evidence = False
                result.irf_count += 1
                if irf.logbook_incomplete_questions.lower() == 'no':
                    result.irf_compliance_count += 1
                if irf.logbook_received is not None:
                    work_days = IndicatorHistory.work_days(irf.date_of_interception, irf.logbook_received, irf.station.operating_country)
                    result.irf_lag_count += 1
                    result.irf_lag_total += work_days
                    result.irf_lag_percent_total += IndicatorsViewSet.score_lag(work_days)
                if irf.verified_evidence_categorization is not None:
                    result.irf_forms_verified += 1
                    if irf.verified_evidence_categorization.lower().startswith('evidence'):
                        result.evidence_count += 1
                    elif irf.verified_evidence_categorization.lower().startswith('should'):
                        result.invalid_intercept_count += 1
                    elif irf.verified_evidence_categorization.lower().startswith('high'):
                        result.high_risk_count += 1
                if irf.evidence_categorization is not None and irf.evidence_categorization.lower().startswith('evidence'):
                    evidence = True
                    
                victims = interceptee_storage.get_form_storage_class().objects.filter(interception_record=irf, person__role='PVOT')
                for victim in victims:
                    result.victim_count += 1
                    if evidence:
                        result.victim_evidence_count += 1
                    if victim.not_physically_present.lower() != 'true':
                        result.victim_present_count += 1
                        if victim.person.photo is not None and victim.person.photo != '':
                            result.photo_count += 1
                    if victim.person.phone_contact is not None and victim.person.phone_contact != '':
                        result.phone_count += 1
                        if victim.person.phone_verified:
                            result.phone_verified_count += 1
                if not irf.verified_evidence_categorization.lower().startswith('should'):
                    suspects = interceptee_storage.get_form_storage_class().objects.filter(interception_record=irf,
                                                                                           person__role='Suspect',
                                                                                          not_physically_present=False)
                    for suspect in suspects:
                        result.suspect_present_count += 1
                        if suspect.person.photo is not None and suspect.person.photo != '':
                            result.suspect_photo_count += 1
                    
                    suspects = interceptee_storage.get_form_storage_class().objects.filter(interception_record=irf,
                                                                                           person__role='Suspect')
                    result.suspect_count += len(suspects)
                    
                    IndicatorsViewSet.cif_indicators_for_irf(result, irf)
                    IndicatorsViewSet.vdf_indicators_for_irf(result, irf)
                    IndicatorsViewSet.pvf_indicators_for_irf(result, irf)
                    IndicatorsViewSet.sf_indicators_for_irf(result, irf)
                    IndicatorsViewSet.lf_indicators_for_irf(result, irf)
            
            gsps = Gospel.objects.filter(station=station, date_time_entered_into_system__date__gte=start_date,  date_time_entered_into_system__date__lte=end_date)
            result.gsp_count += len(gsps)
                
            if station.open or result.irf_count > 0:
                # only include stations that are open or have IRFs present in the time period
                result.compute_values(pvf_form)
                results.append(result)
        
        total_result = CollectionResults('Totals')
        total_result.sum_list(results)
        total_result.compute_values(pvf_form)
        total_result.pvf_form = pvf_form
        
        all_results = [total_result.__dict__]
        for result in results:
            all_results.append(result.__dict__)
        
        return all_results
     
    @staticmethod
    def cifs_for_irf(irf):
        results = []
        form = Form.current_form('CIF', irf.station.id)
        if form is None:
            return results
        
        match_pattern = irf.irf_number + "(\\.[0-9]+|[A-Z])$"
        cifs = form.storage.get_form_storage_class().objects.filter(cif_number__startswith=irf.irf_number)
        for cif in cifs:  
            match = re.match(match_pattern, cif.cif_number)
            if match is None:
                continue
            
            results.append(cif)
        
        return results 
            
    @staticmethod        
    def cif_indicators_for_irf(result, irf):
        form = Form.current_form('CIF', irf.station.id)
        if form is None:
            return
        
        match_pattern = irf.irf_number + "(\\.[0-9]+|[A-Z])$"
        cifs = form.storage.get_form_storage_class().objects.filter(cif_number__startswith=irf.irf_number)
        for cif in cifs:
            match = re.match(match_pattern, cif.cif_number)
            if match is None:
                continue
            
            result.cif_count += 1
            if cif.logbook_incomplete_questions.lower() == 'no':
                result.cif_compliance_count += 1
            if cif.interview_date is not None and cif.logbook_received is not None:
                work_days = IndicatorHistory.work_days(cif.interview_date, cif.logbook_received, cif.station.operating_country)
                result.cif_lag_count += 1
                result.cif_lag_total += work_days
                result.cif_lag_percent_total += IndicatorsViewSet.score_lag(work_days)
            if irf.evidence_categorization is not None and (irf.evidence_categorization.lower().startswith('evidence')):
                        result.cif_with_evidence_count += 1
    @staticmethod
    def vdfs_for_irf(irf):
        results = []
        form = Form.current_form('VDF', irf.station.id)
        if form is None:
            return results
        
        match_pattern = irf.irf_number + "[A-Z]{1,2}$"
        vdfs = form.storage.get_form_storage_class().objects.filter(vdf_number__startswith=irf.irf_number)
        for vdf in vdfs:  
            match = re.match(match_pattern, vdf.vdf_number)
            if match is None:
                continue
            
            results.append(vdf)
        
        return results
    
    @staticmethod
    def pvfs_for_irf(irf):
        results = []
        form = Form.current_form('PVF', irf.station.id)
        if form is None:
            return results
        
        match_pattern = irf.irf_number + "[A-Z]{1,2}$"
        vdfs = form.storage.get_form_storage_class().objects.filter(vdf_number__startswith=irf.irf_number, status="approved")
        for vdf in vdfs:  
            match = re.match(match_pattern, vdf.vdf_number)
            if match is None:
                continue
            
            results.append(vdf)
        
        return results
    
    @staticmethod
    def sfs_for_irf(irf):
        results = []
        form = Form.current_form('SF', irf.station.id)
        if form is None:
            return results
        
        match_pattern = irf.irf_number + "[A-Z]{1,2}$"
        sfs = form.storage.get_form_storage_class().objects.filter(sf_number__startswith=irf.irf_number, status="approved")
        for sf in sfs:  
            match = re.match(match_pattern, sf.sf_number)
            if match is None:
                continue
            
            results.append(sf)
        incident = Incident.objects.get(incident_number=irf.irf_number)
        sfs = form.storage.get_form_storage_class().objects.filter(associated_incidents=incident)
        for sf in sfs:  
            results.append(sf)
        
        return results
    
    @staticmethod
    def lfs_for_irf(irf):
        results = []
        form = Form.current_form('LF', irf.station.id)
        if form is None:
            return results
        
        match_pattern = irf.irf_number + "[A-Z]{1,2}$"
        lfs = form.storage.get_form_storage_class().objects.filter(lf_number__startswith=irf.irf_number, status="approved")
        for lf in lfs:  
            match = re.match(match_pattern, lf.lf_number)
            if match is None:
                continue
            
            results.append(lf)
        
        return results 
    
    @staticmethod
    def vdf_indicators_for_irf(result, irf):
        form = Form.current_form('VDF', irf.station.id)
        if form is None:
            return

        match_pattern = irf.irf_number + "[A-Z]{1,2}$"
        vdfs = form.storage.get_form_storage_class().objects.filter(vdf_number__startswith=irf.irf_number)
        for vdf in vdfs:
            match = re.match(match_pattern, vdf.vdf_number)
            if match is None:
                continue
            
            result.vdf_count += 1
            if vdf.logbook_incomplete_questions.lower() == 'no':
                result.vdf_compliance_count += 1
            if vdf.interview_date is not None and vdf.logbook_received is not None:
                work_days = IndicatorHistory.work_days(vdf.interview_date, vdf.logbook_received, vdf.station.operating_country)
                result.vdf_lag_count += 1
                result.vdf_lag_total += work_days
                result.vdf_lag_percent_total += IndicatorsViewSet.score_lag(work_days)
            
    
    @staticmethod
    def pvf_indicators_for_irf(result, irf):
        form = Form.current_form('PVF', irf.station.id)
        if form is None:
            return

        match_pattern = irf.irf_number + "[A-Z]{1,2}$"
        vdfs = form.storage.get_form_storage_class().objects.filter(vdf_number__startswith=irf.irf_number)
        for vdf in vdfs:
            match = re.match(match_pattern, vdf.vdf_number)
            if match is None:
                continue
            
            result.vdf_count += 1
            if vdf.logbook_incomplete_questions.lower() == 'no':
                result.vdf_compliance_count += 1
            if vdf.interview_date is not None and vdf.logbook_received is not None:
                work_days = IndicatorHistory.work_days(vdf.interview_date, vdf.logbook_received, vdf.station.operating_country)
                result.vdf_lag_count += 1
                result.vdf_lag_total += work_days
                result.vdf_lag_percent_total += IndicatorsViewSet.score_lag(work_days)
            if vdf.staff_share_gospel is not None and vdf.staff_share_gospel.lower() == 'yes':
                result.vdf_gospel_count += 1
            if vdf.what_victim_believes_now != 'Already believes Jesus is the one true God':
                result.profession_denominator += 1
            IndicatorsViewSet.gospel_indicators_for_vdf(result, vdf)
    
    @staticmethod        
    def sf_indicators_for_irf(result, irf):
        form = Form.current_form('SF', irf.station.id)
        if form is None:
            return
        
        match_pattern = irf.irf_number + "(\\.[0-9]+|[A-Z])$"
        sfs = form.storage.get_form_storage_class().objects.filter(sf_number__startswith=irf.irf_number)
        for sf in sfs:  
            match = re.match(match_pattern, sf.sf_number)
            if match is None:
                continue
            
            result.sf_count += 1
            if sf.logbook_incomplete_questions.lower() == 'no':
                result.sf_compliance_count += 1
            infos = SuspectInformation.objects.filter(suspect=sf).order_by('id')
            if len(infos) > 0 and infos[0].interview_date is not None and sf.logbook_received is not None:
                work_days = IndicatorHistory.work_days(infos[0].interview_date, sf.logbook_received, sf.station.operating_country)
                result.sf_lag_count += 1
                result.sf_lag_total += work_days
                result.sf_lag_percent_total += IndicatorsViewSet.score_lag(work_days)
        
        incident = Incident.objects.get(incident_number=irf.irf_number)
        sfs = form.storage.get_form_storage_class().objects.filter(associated_incidents=incident)
        for sf in sfs:  
            result.sf_count += 1
            if sf.logbook_incomplete_questions.lower() == 'no':
                result.sf_compliance_count += 1
    
    @staticmethod        
    def lf_indicators_for_irf(result, irf):
        form = Form.current_form('LF', irf.station.id)
        if form is None:
            return
        
        match_pattern = irf.irf_number + "(\\.[0-9]+|[A-Z])$"
        lfs = form.storage.get_form_storage_class().objects.filter(lf_number__startswith=irf.irf_number)
        for lf in lfs:  
            match = re.match(match_pattern, lf.lf_number)
            if match is None:
                continue
            
            result.lf_count += 1
            if lf.logbook_incomplete_questions.lower() == 'no':
                result.lf_compliance_count += 1
            infos = LocationInformation.objects.filter(lf=lf).order_by('id')
            if len(infos) > 0 and infos[0].interview_date is not None and lf.logbook_received is not None:
                work_days = IndicatorHistory.work_days(infos[0].interview_date, lf.logbook_received, lf.station.operating_country)
                result.lf_lag_count += 1
                result.lf_lag_total += work_days
                result.lf_lag_percent_total += IndicatorsViewSet.score_lag(work_days)
    
    @staticmethod        
    def gospel_indicators_for_vdf(result, vdf):
        gospel_verifications = GospelVerification.objects.filter(vdf=vdf, date_of_followup__isnull=False)
        for gospel_verification in gospel_verifications:
            result.gospel_verification_count += 1
            if vdf.what_victim_believes_now == 'Came to believe that Jesus is the one true God':
                result.gospel_profession_count += 1
            work_days = IndicatorHistory.work_days(vdf.logbook_submitted, gospel_verification.date_of_followup, gospel_verification.station.operating_country)
            result.gospel_lag_total += work_days
            result.gospel_lag_count += 1
            result.gospel_lag_percent_total += IndicatorsViewSet.score_lag(work_days) 
        
    
    def getVictimDetail(self, start_date, end_date, project_code, country_id, detail_data):
        victims = IntercepteeCommon.objects.filter(
                person__role='PVOT',
                interception_record__station__operating_country__id=country_id,
                interception_record__verified_date__gte=start_date,
                interception_record__verified_date__lte=end_date).exclude(not_physically_present__iexact='true').order_by('person__full_name')
        
        if project_code != 'Totals':
            victims = victims.filter(interception_record__station__station_code = project_code)
        table_data = {
            'labels': ['Victim Name', 'IRF Number', 'Evidence', 'Phone Number', 'Verified Phone Number', 'Photo' ],
            'rows': []
            }
        with_evidence_count = 0;
        with_phone_count = 0
        with_phone_verified = 0
        with_photo = 0
        for victim in victims:
            row = []
            row.append({'value': victim.person.full_name})
            row.append({'value': victim.interception_record.irf_number})
            if victim.interception_record.evidence_categorization is not None and victim.interception_record.evidence_categorization.lower().startswith('evidence'):
                row.append({'value': 'Yes'})
                with_evidence_count += 1
            else:
                row.append({'value': 'No'})
            if victim.person.phone_contact is not None and victim.person.phone_contact != '':
                row.append({'value': 'Yes'})
                with_phone_count += 1
                if victim.person.phone_verified:
                    row.append({'value': 'Yes'})
                    with_phone_verified += 1
                else:
                    row.append({'value': 'No'})
            else:
                row.append({'value': 'No'})
                row.append({'value': ''})
            if victim.person.photo is not None and victim.person.photo != '':
                row.append({'value': 'Yes'})
                with_photo += 1
            else:
                row.append({'value': 'No'})
            table_data['rows'].append(row)

        photo_percentage = str(with_photo * 100 / len(victims)) if len(victims) > 0 else ''
        detail_data['table_data'] = table_data
        detail_data['text'].append('# PVs: ' + str(len(victims)))
        detail_data['text'].append('PVs with evidence: ' + str(with_evidence_count))
        detail_data['text'].append('PVs with phone number: ' + str(with_phone_count))
        detail_data['text'].append('PVs with phone number verified: ' + str(with_phone_verified))
        detail_data['text'].append('PVs with photo: ' + str(with_photo))
        detail_data['text'].append('PV Photos %: ' + photo_percentage)
        
    
    def getSuspectDetail(self, start_date, end_date, project_code, country_id, detail_data):
        suspects = IntercepteeCommon.objects.filter(
                person__role='Suspect',
                interception_record__station__operating_country__id=country_id,
                interception_record__verified_date__gte=start_date,
                interception_record__verified_date__lte=end_date).exclude(not_physically_present__iexact='true').order_by('person__full_name')
        
        if project_code != 'Totals':
            suspects = suspects.filter(interception_record__station__station_code = project_code)
        table_data = {
            'labels': ['Suspect Name', 'IRF Number',  'Photo' ],
            'rows': []
            }
        
        with_photo = 0
        for suspect in suspects:
            row = []
            row.append({'value': suspect.person.full_name})
            row.append({'value': suspect.interception_record.irf_number})
            if suspect.person.photo is not None and suspect.person.photo != '':
                row.append({'value': 'Yes'})
                with_photo += 1
            else:
                row.append({'value': 'No'})
            table_data['rows'].append(row)

        photo_percentage = str(with_photo * 100 / len(suspects)) if len(suspects) > 0 else ''
        detail_data['table_data'] = table_data
        detail_data['text'].append('# Suspects: ' + str(len(suspects)))
        detail_data['text'].append('Suspects with photo: ' + str(with_photo))
        detail_data['text'].append('S Photos %: ' + photo_percentage)
    
    def getIrfDetailList(self, start_date, end_date, project_code, country_id):
        irfs = IrfCommon.objects.filter(station__operating_country__id=country_id, verified_date__gte=start_date,
                                 verified_date__lte=end_date).exclude(evidence_categorization__startswith='Should')
        if project_code != 'Totals':
            irfs = irfs.filter(station__station_code = project_code)
        return irfs
        
    def getIrfDetail(self, start_date, end_date, project_code, country_id, detail_data):
        irfs = self.getIrfDetailList(start_date, end_date, project_code, country_id)
        table_data = {
            'labels': ['IRF Number', 'Compliant', 'Lag Time', 'Lag Score', 'Initial Evidence Category', 'Verified Evidence Category'],
            'rows': []
            }
        
        total_work_days = 0
        compliant_count = 0
        lag_total_score = 0
        for irf in irfs:
            row = []
            row.append({'value': irf.irf_number})
            if irf.logbook_incomplete_questions.lower() == 'no':
                compliant_count += 1
                row.append({'value': 'Yes'})
            else:
                row.append({'value': 'No'})
            work_days = IndicatorHistory.work_days(irf.date_of_interception, irf.logbook_received, irf.station.operating_country)
            total_work_days += work_days
            row.append({'value': work_days})
            lag_score = self.score_lag(work_days)
            lag_total_score += lag_score
            row.append({'value': lag_score})
            row.append({'value': irf.evidence_categorization})
            row.append({'value': irf.verified_evidence_categorization})
            table_data['rows'].append(row)
        
        detail_data['table_data'] = table_data
        if len(irfs) > 0:
            detail_data['text'].append('# IRFs = ' + str(len(irfs)))
            detail_data['text'].append('# IRFs in Compliance = ' + str(compliant_count))
            detail_data['text'].append('Average IRF collection lag time = ' + str(math.floor(total_work_days/len(irfs) + 0.5)))
            detail_data['text'].append('Average IRF collection lag score = ' + str(math.floor(lag_total_score/len(irfs) + 0.5)))
    
    def getIntercepteeDetail(self, start_date, end_date, project_code, country_id, detail_data):
        irfs = self.getIrfDetailList(start_date, end_date, project_code, country_id)
        table_data = {
            'labels': ['IRF Number', '#PVFs / # PVs', '# SFs / # Suspects'],
            'rows': []
            }
        
       
        total_pvots = 0
        total_suspects = 0
        total_pvfs = 0
        total_sfs = 0
        for irf in irfs:
            if irf.verified_evidence_categorization.lower().startswith('should'):
                continue
            row = []
            pvot = 0
            suspect = 0
            interceptees = IntercepteeCommon.objects.filter(interception_record=irf)
            for interceptee in interceptees:
                if interceptee.person.role == 'PVOT':
                    pvot += 1
                elif interceptee.person.role == 'Suspect':
                    suspect += 1
            
            pvfs = IndicatorsViewSet.pvfs_for_irf(irf)
            sfs = IndicatorsViewSet.sfs_for_irf(irf)
            
            row.append({'value':irf.irf_number})
            if len(pvfs) != pvot:
                row.append({'value':str(len(pvfs)) + ' / ' + str(pvot) + ' **'})
            else:
                row.append({'value':str(len(pvfs)) + ' / ' + str(pvot)})
            if len(sfs) != suspect:
                row.append({'value':str(len(sfs)) + ' / ' + str(suspect) + ' **'})
            else:
                row.append({'value':str(len(sfs)) + ' / ' + str(suspect)})
            total_pvots += pvot
            total_suspects += suspect
            total_pvfs += len(pvfs)
            total_sfs += len(sfs)
            
            table_data['rows'].append(row)
        
        detail_data['table_data'] = table_data
        if len(detail_data['table_data']['rows']) > 0:
             detail_data['text'].append('# PVFs = ' + str(total_pvfs))
             detail_data['text'].append('# PVs = ' + str(total_pvots))
             detail_data['text'].append('# SFs = ' + str(total_sfs))
             detail_data['text'].append('# Suspects = ' + str(total_suspects))

    def getCifDetail(self, start_date, end_date, project_code, country_id, detail_data):
        irfs = self.getIrfDetailList(start_date, end_date, project_code, country_id)
        table_data = {
            'labels': ['CIF Number', 'Compliant', 'Lag Time', 'Lag Score','Evidence'],
            'rows': []
            }
        
        cif_count = 0
        total_work_days = 0
        with_evidence_count = 0
        lag_count = 0
        lag_total_score = 0
        compliant_count = 0
        for irf in irfs:
            cifs = IndicatorsViewSet.cifs_for_irf(irf)
            for cif in cifs:
                cif_count += 1
                row = []
                row.append({'value': cif.cif_number})
                if cif.logbook_incomplete_questions.lower() == 'no':
                    compliant_count += 1
                    row.append({'value': 'Yes'})
                else:
                    row.append({'value': 'No'})
                if cif.interview_date is not None and cif.logbook_received is not None:
                    work_days = IndicatorHistory.work_days(cif.interview_date, cif.logbook_received, cif.station.operating_country)
                    total_work_days += work_days
                    lag_total_score += self.score_lag(work_days)
                    lag_count += 1
                    row.append({'value': work_days})
                    row.append({'value': self.score_lag(work_days)})
                else:
                    row.append({'value': 'Missing date(s)'})
                    row.append({'value': ''})
                if irf.evidence_categorization is not None and irf.evidence_categorization.lower().startswith('evidence'):
                    row.append({'value': 'Yes'})
                    with_evidence_count += 1
                else:
                    row.append({'value': 'No'})
                table_data['rows'].append(row)
        
        detail_data['table_data'] = table_data
        if len(detail_data['table_data']['rows']) > 0:
            detail_data['text'].append('# CIFs = ' + str(cif_count))
            detail_data['text'].append('# CIFs in Compliance = ' + str(compliant_count))
            detail_data['text'].append('Average CIF collection lag time = ' + str(math.floor(total_work_days/lag_count + 0.5)))
            detail_data['text'].append('Average CIF collection lag score = ' + str(math.floor(lag_total_score/lag_count + 0.5)))
            detail_data['text'].append('CIFs with evidence count: ' + str(with_evidence_count))
    
    def getVdfDetail(self, start_date, end_date, project_code, country_id, detail_data):
        irfs = self.getIrfDetailList(start_date, end_date, project_code, country_id)
        table_data = {
            'labels': ['VDF Number', 'Compliant', 'Lag Time', 'Lag Score'],
            'rows': []
            }
        vdf_count = 0
        compliant_count = 0
        total_work_days = 0
        lag_count = 0
        lag_total_score = 0
        for irf in irfs:
            vdfs = IndicatorsViewSet.vdfs_for_irf(irf)
            for vdf in vdfs:
                vdf_count += 1
                row = []
                row.append({'value': vdf.vdf_number})
                if vdf.logbook_incomplete_questions.lower() == 'no':
                    compliant_count += 1
                    row.append({'value': 'Yes'})
                else:
                    row.append({'value': 'No'})
                if vdf.interview_date is not None and vdf.logbook_received is not None:
                    work_days = IndicatorHistory.work_days(vdf.interview_date, vdf.logbook_received, vdf.station.operating_country)
                    total_work_days += work_days
                    lag_total_score += self.score_lag(work_days)
                    lag_count += 1
                    row.append({'value': work_days})
                    row.append({'value': self.score_lag(work_days)})
                else:
                    row.append({'value': 'Missing date(s)'})
                    row.append({'value': ''})
                table_data['rows'].append(row)
        
        detail_data['table_data'] = table_data
        if len(detail_data['table_data']['rows']) > 0:
            detail_data['text'].append('# of VDFs = ' + str(vdf_count))
            detail_data['text'].append('# VDFs in Compliance = ' + str(compliant_count))
            detail_data['text'].append('Average VDF collection lag time = ' + str(math.floor(total_work_days/lag_count + 0.5)))
            detail_data['text'].append('Average VDF collection lag score = ' + str(math.floor(lag_total_score/lag_count + 0.5)))
    
    def getPvfDetail(self, start_date, end_date, project_code, country_id, detail_data):
        irfs = self.getIrfDetailList(start_date, end_date, project_code, country_id)
        table_data = {
            'labels': ['PVF Number', 'Compliant', 'Lag Time', 'Lag Score'],
            'rows': []
            }
        pvf_count = 0
        compliant_count = 0
        total_work_days = 0
        lag_count = 0
        lag_total_score = 0
        for irf in irfs:
            pvfs = IndicatorsViewSet.pvfs_for_irf(irf)
            for pvf in pvfs:
                pvf_count += 1
                row = []
                row.append({'value': pvf.vdf_number})
                if pvf.logbook_incomplete_questions.lower() == 'no':
                    compliant_count += 1
                    row.append({'value': 'Yes'})
                else:
                    row.append({'value': 'No'})
                if pvf.interview_date is not None and pvf.logbook_received is not None:
                    work_days = IndicatorHistory.work_days(pvf.interview_date, pvf.logbook_received, pvf.station.operating_country)
                    total_work_days += work_days
                    lag_total_score += self.score_lag(work_days)
                    lag_count += 1
                    row.append({'value': work_days})
                    row.append({'value': self.score_lag(work_days)})
                else:
                    row.append({'value': 'Missing date(s)'})
                    row.append({'value': ''})
                table_data['rows'].append(row)
        
        detail_data['table_data'] = table_data
        if len(detail_data['table_data']['rows']) > 0:
            detail_data['text'].append('# of PVFs = ' + str(pvf_count))
            detail_data['text'].append('# PVFs in Compliance = ' + str(compliant_count))
            detail_data['text'].append('Average PVF collection lag time = ' + str(math.floor(total_work_days/lag_count + 0.5)))
            detail_data['text'].append('Average PVF collection lag score = ' + str(math.floor(lag_total_score/lag_count + 0.5)))
            
    def getSfDetail(self, start_date, end_date, project_code, country_id, detail_data):
        irfs = self.getIrfDetailList(start_date, end_date, project_code, country_id)
        table_data = {
            'labels': ['SF Number', 'Compliant', 'Lag Time', 'Lag Score'],
            'rows': []
            }
        sf_count = 0
        compliant_count = 0
        total_work_days = 0
        lag_count = 0
        lag_total_score = 0
        for irf in irfs:
            sfs = IndicatorsViewSet.sfs_for_irf(irf)
            for sf in sfs:
                sf_count += 1
                row = []
                row.append({'value': sf.sf_number})
                if sf.logbook_incomplete_questions.lower() == 'no':
                    compliant_count += 1
                    row.append({'value': 'Yes'})
                else:
                    row.append({'value': 'No'})
                infos = SuspectInformation.objects.filter(suspect=sf).order_by('id')
                if len(infos) > 0 and infos[0].interview_date is not None and sf.logbook_received is not None:
                    work_days = IndicatorHistory.work_days(infos[0].interview_date, sf.logbook_received, sf.station.operating_country)
                    total_work_days += work_days
                    lag_total_score += self.score_lag(work_days)
                    lag_count += 1
                    row.append({'value': work_days})
                    row.append({'value': self.score_lag(work_days)})
                else:
                    row.append({'value': 'Missing date(s)'})
                    row.append({'value': ''})
                table_data['rows'].append(row)
        
        detail_data['table_data'] = table_data
        if len(detail_data['table_data']['rows']) > 0:
            detail_data['text'].append('# of SFs = ' + str(sf_count))
            detail_data['text'].append('# SFs in Compliance = ' + str(compliant_count))
            detail_data['text'].append('Average SF collection lag time = ' + str(math.floor(total_work_days/lag_count + 0.5)))
            detail_data['text'].append('Average SF collection lag score = ' + str(math.floor(lag_total_score/lag_count + 0.5)))
    
    def getLfDetail(self, start_date, end_date, project_code, country_id, detail_data):
        irfs = self.getIrfDetailList(start_date, end_date, project_code, country_id)
        table_data = {
            'labels': ['SF Number', 'Compliant', 'Lag Time', 'Lag Score'],
            'rows': []
            }
        lf_count = 0
        compliant_count = 0
        total_work_days = 0
        lag_count = 0
        lag_total_score = 0
        for irf in irfs:
            lfs = IndicatorsViewSet.lfs_for_irf(irf)
            for lf in lfs:
                lf_count += 1
                row = []
                row.append({'value': lf.lf_number})
                if lf.logbook_incomplete_questions.lower() == 'no':
                    compliant_count += 1
                    row.append({'value': 'Yes'})
                else:
                    row.append({'value': 'No'})
                infos = LocationInformation.objects.filter(lf=lf).order_by('id')
                if len(infos) > 0 and infos[0].interview_date is not None and lf.logbook_received is not None:
                    work_days = IndicatorHistory.work_days(infos[0].interview_date, lf.logbook_received, lf.station.operating_country)
                    total_work_days += work_days
                    lag_total_score += self.score_lag(work_days)
                    lag_count += 1
                    row.append({'value': work_days})
                    row.append({'value': self.score_lag(work_days)})
                else:
                    row.append({'value': 'Missing date(s)'})
                    row.append({'value': ''})
                table_data['rows'].append(row)
        
        detail_data['table_data'] = table_data
        if len(detail_data['table_data']['rows']) > 0:
            detail_data['text'].append('# of SFs = ' + str(lf_count))
            detail_data['text'].append('# SFs in Compliance = ' + str(compliant_count))
            detail_data['text'].append('Average SF collection lag time = ' + str(math.floor(total_work_days/lag_count + 0.5)))
            detail_data['text'].append('Average SF collection lag score = ' + str(math.floor(lag_total_score/lag_count + 0.5)))
    
    def getGospelDetail(self, start_date, end_date, project_code, country_id, detail_data):
        irfs = self.getIrfDetailList(start_date, end_date, project_code, country_id).order_by('irf_number')
        table_data = {
            'labels': ['VDF Number', 'Date Verified', 'Verified Profession', 'Lag Time'],
            'rows': []
            }
        for irf in irfs:
            form = Form.current_form('PVF', irf.station.id)
            if form is None:
                return
    
            match_pattern = irf.irf_number + "[A-Z]{1,2}$"
            vdfs = form.storage.get_form_storage_class().objects.filter(vdf_number__startswith=irf.irf_number)
            for vdf in vdfs:
                match = re.match(match_pattern, vdf.vdf_number)
                if match is None:
                    continue
                
                gospel_verifications = GospelVerification.objects.filter(vdf=vdf)
                for gospel_verification in gospel_verifications:
                    row = []
                    row.append({'value':vdf.vdf_number})
                    row.append({'value':gospel_verification.date_of_followup})
                    if gospel_verification.date_of_followup is not None:
                        if vdf.what_victim_believes_now == 'Came to believe that Jesus is the one true God':
                            row.append({'value':'Yes'})
                        else:
                            row.append({'value':'No'})
                        work_days = IndicatorHistory.work_days(vdf.logbook_submitted, gospel_verification.date_of_followup, gospel_verification.station.operating_country)
                        row.append({'value':work_days})
                    else:
                        row.append({'value':"N/A"})
                        row.append({'value':"N/A"})
                    
                    table_data['rows'].append(row)
        
        detail_data['table_data'] = table_data
        
    
    def collection_details(self, request):
        start_date = request.GET['start_date']
        end_date = request.GET['end_date']
        type = request.GET['type']
        country_id = request.GET['country_id']
        project_code = request.GET['project']
        
        detail_data = {
            'header':"Details for " + type + " for project " + project_code,
            'text': [],
            'table_data': None
            }
             
        function_dict = {
            '# PVs':self.getVictimDetail,
            'IRFs':self.getIrfDetail,
            'IRFs in Compliance #':self.getIrfDetail,
            'IRF Collection Lag Time':self.getIrfDetail,
            'CIFs':self.getCifDetail,
            'CIFs in Compliance #':self.getCifDetail,
            'CIF Collection Lag Time':self.getCifDetail,
            'CIFs with Evidence #':self.getCifDetail,
            'VDFs':self.getVdfDetail,
            'VDFs in Compliance #':self.getVdfDetail,
            'VDF Collection Lag Time':self.getVdfDetail,
            'PVFs':self.getPvfDetail,
            'PVFs in Compliance #':self.getPvfDetail,
            'PVF Collection Lag Time':self.getPvfDetail,
            'SFs':self.getSfDetail,
            'SFs in Compliance #':self.getSfDetail,
            'SF Collection Lag Time':self.getSfDetail,
            'LFs':self.getLfDetail,
            'LFs in Compliance #':self.getLfDetail,
            'LF Collection Lag Time':self.getLfDetail,
            'Total # Verified Forms':self.getIrfDetail,
            'Evidence of Trafficking':self.getIrfDetail,
            'Evidence of Trafficking %':None,
            'Invalid Intercept':self.getIrfDetail,
            'Invalid Intercept %':None,
            'High Risk of Trafficking':self.getIrfDetail,
            'High Risk of Trafficking %':None,
            'PV Photos %':self.getVictimDetail,
            'S Photos %':self.getSuspectDetail,
            'IRF Suspect SF %':self.getIntercepteeDetail,
            'PVF %':self.getIntercepteeDetail,
            'Gospel Verifications #':self.getGospelDetail,
            'Gospel Verification Lag Time':self.getGospelDetail,
            };
        
        if type in function_dict and function_dict[type] is not None:
            function_dict[type](start_date, end_date, project_code, country_id, detail_data)
        else:
            detail_data['text'].append('No Details for type ' + type)
        
        return Response(detail_data)
            
            