import logging
import os

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings

from dataentry.models import BorderStation, Form, FormCategory

class IndicatorsViewSet(viewsets.ViewSet):
    def get_class(self, type, station):
        if getattr(self, 'class_cache', None) is None:
            self.class_cache = {
                'IRF':{},
                'Interceptee':{},
                'CIF':{},
                'VDF':{}
                }
        
        if station in self.class_cache[type]:
            the_class = self.class_cache[type][station]
        else:
            if type != 'Interceptee':
                form = Form.current_form(type, station.id)
                if form is None:
                    the_class = None
                else:
                    the_class = form.storage.get_form_storage_class()
            else:
                form = Form.current_form('IRF', station.id)
                form_categories = FormCategory.objects.filter(form=form, name='Interceptees')
                if len(form_categories) == 1 and form_categories[0].storage is not None:
                    the_class = form_categories[0].storage.get_form_storage_class()
                else:
                    the_class = None

            self.class_cache[type][station] = the_class
        
        return the_class
            
    def calculate_indicators(self, request):
        in_country = self.request.GET.get('country_ids')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        if start_date is None or end_date is None:
            ret = {
                    'errors': 'start and end dates must be provided',
                }
            return Response (ret, status=status.HTTP_400_BAD_REQUEST)
        
        if in_country is not None and in_country != '':
            country_id_list = []
            for cntry in in_country.split(','):
                country_id_list.append(int(cntry))
            station_list = BorderStation.objects.filter(operating_country__id__in=country_id_list)
        else:
            station_list = BorderStation.objects.all()
        
        forms_processed = []
        
        results = {}
        
        form_method = {
            'IRF':self.calculate_irf_indicators,
            'CIF':self.calculate_cif_indicators,
            'VDF':self.calculate_vdf_indicators,
            }
        
        # general form information
        for form_type in ['IRF','CIF','VDF']:
            for station in station_list:
                form_class = self.get_class(form_type, station)
                if form_class is None or form_class in forms_processed:
                    # If there is no form for this station or we have already processed the form
                    # associated with this station, then skip to the next station
                    continue;
                
                query_set = form_class.objects.filter(station__in=station_list,
                                        logbook_submitted__gte=start_date, logbook_submitted__lte=end_date)
                form_method[form_type](results, query_set)
                
                if form_type == 'IRF':
                    query_set = form_class.objects.filter(station__in=station_list,
                                        logbook_first_verification_date__gte=start_date,
                                        logbook_first_verification_date__lte=end_date)
                    self.calculate_irf_first_verification(results, query_set)
                    
                    query_set = form_class.objects.filter(station__in=station_list,
                                        logbook_second_verification_date__gte=start_date,
                                        logbook_second_verification_date__lte=end_date)
                    self.calculate_irf_second_verification(results, query_set)
                    
                forms_processed.append(form_class)
        
        self.process_photos(results, station_list, start_date, end_date)
        return Response(results)
    
    def date_present(self, the_date_value):
        if the_date_value is not None and the_date_value != '':
            return True
        
        return False
    
    def work_days (self, start_date, end_date):
        days_offset = [
                [0,1,2,3,4,4,4],
                [0,1,2,3,3,3,4],
                [0,1,2,2,2,3,4],
                [0,1,1,1,2,3,4],
                [0,0,0,1,2,3,4],
                [0,0,0,1,2,3,4],
                [0,0,1,2,3,4,4]
            ]
        
        if end_date <= start_date:
            return 0
        
        days = (end_date - start_date).days
        weeks = int(days/7)
        partial = days - weeks * 7
        work_days = weeks * 5 + days_offset[start_date.weekday()][partial]
        
        return work_days
    
    def add_result(self, result, name, value):
        if name in result:
            result[name] = result[name] + value
        else:
            result[name] = value

    def calculate_irf_indicators(self, results, query_set):
        submitted_count = 0
        total_lag = 0
        interceptee_count = 0
        interceptee_photo_count = 0
        need_1v = 0
        need_2v = 0
            
        for irf in query_set:
            submitted_count += 1
            
            if not self.date_present(irf.logbook_first_verification_date):
                need_1v += 1
            
            if not self.date_present(irf.logbook_first_verification_date):
                need_2v += 1
            
            if self.date_present(irf.logbook_information_complete):
                start_date = irf.logbook_information_complete
            elif self.date_present(irf.logbook_received):
                start_date = irf.logbook_received
            else:
                start_date = irf.date_time_entered_into_system.date()
            
            total_lag += self.work_days(start_date, irf.logbook_submitted)
            
            interceptee_class = self.get_class('Interceptee', irf.station)
            if interceptee_class is not None:
                interceptees = interceptee_class.objects.filter(interception_record=irf)
                interceptee_count += len(interceptees)
                for interceptee in interceptees:
                    if interceptee.photo is not None and interceptee.photo != '':
                        interceptee_photo_count += 1
        
        self.add_result(results, 'irfSubmittedCount', submitted_count)
        self.add_result(results, 'irfTotalLag', total_lag)
        self.add_result(results, 'intercepteeCount', interceptee_count)
        self.add_result(results, 'intercepteePhotoCount', interceptee_photo_count)
        self.add_result(results, 'need_first_verification', need_1v)
        self.add_result(results, 'need_second_verification', need_1v)

    def calculate_irf_first_verification(self, results, query_set):
        clear_count = 0
        some_count = 0
        high_count = 0
        snhi_count = 0
        
        lag_time = 0
        lag_count = 0
        follow_up = 0
        
        for irf in query_set:
            if irf.logbook_first_verification.startswith('Clear'):
                clear_count += 1
            elif irf.logbook_first_verification.startswith('Some'):
                some_count += 1
            elif irf.logbook_first_verification.startswith('High'):
                high_count += 1
            elif irf.logbook_first_verification.startswith('Should not'):
                snhi_count += 1
            
            if self.date_present(irf.logbook_information_complete):
                lag_count += 1
                lag_time += self.work_days(irf.logbook_information_complete, irf.logbook_first_verification_date)
                
            if irf.logbook_followup_call == 'Yes':
                follow_up += 1
        
        self.add_result(results, 'clearCount1v', clear_count)
        self.add_result(results, 'someCount1v', some_count)
        self.add_result(results, 'highCount1v', high_count)
        self.add_result(results, 'snhiCount1v', snhi_count)
        self.add_result(results, 'lagTime1v', lag_time)
        self.add_result(results, 'lagCount1v', lag_count)
        self.add_result(results, 'followUp', follow_up)
        
    
    def calculate_irf_second_verification(self, results, query_set):
        clear_count = 0
        some_count = 0
        high_count = 0
        snhi_count = 0
        
        clear_count_1v = 0
        some_count_1v = 0
        high_count_1v = 0
        snhi_count_1v = 0
        
        lag_time = 0
        lag_count = 0
        back_corrected = 0
        
        for irf in query_set:
            if irf.logbook_second_verification.startswith('Clear'):
                clear_count += 1
            elif irf.logbook_second_verification.startswith('Some'):
                some_count += 1
            elif irf.logbook_second_verification.startswith('High'):
                high_count += 1
            elif irf.logbook_second_verification.startswith('Should not'):
                snhi_count += 1
            
            if irf.logbook_first_verification.startswith('Clear'):
                clear_count_1v += 1
            elif irf.logbook_first_verification.startswith('Some'):
                some_count_1v += 1
            elif irf.logbook_first_verification.startswith('High'):
                high_count_1v += 1
            elif irf.logbook_first_verification.startswith('Should not'):
                snhi_count_1v += 1
            
            if self.date_present(irf.logbook_information_complete):
                lag_count += 1
                lag_time += self.work_days(irf.logbook_information_complete, irf.logbook_second_verification_date)
                
            if irf.logbook_back_corrected is not None and irf.logbook_back_corrected != '':
                back_corrected += 1
        
        self.add_result(results, 'clearCount2v', clear_count)
        self.add_result(results, 'someCount2v', some_count)
        self.add_result(results, 'highCount2v', high_count)
        self.add_result(results, 'snhiCount2v', snhi_count)
        self.add_result(results, 'clearCount2v1v', clear_count_1v)
        self.add_result(results, 'someCount2v1v', some_count_1v)
        self.add_result(results, 'highCount2v1v', high_count_1v)
        self.add_result(results, 'snhiCount2v1v', snhi_count_1v)
        self.add_result(results, 'lagTime2v', lag_time)
        self.add_result(results, 'lagCount2v', lag_count)
        self.add_result(results, 'backCorrected', back_corrected)
     
    def calculate_form_indicators (self, results, query_set, prefix):
        submitted_count = 0
        total_lag = 0
        interceptee_count = 0
        interceptee_photo_count = 0
        
        for entry in query_set:
            submitted_count += 1
            
            if self.date_present(entry.logbook_information_complete):
                start_date = entry.logbook_information_complete
            elif self.date_present(entry.logbook_received):
                start_date = entry.logbook_received
            else:
                start_date = entry.date_time_entered_into_system.date()
            
            total_lag += self.work_days(start_date, entry.logbook_submitted)
        
        self.add_result(results, prefix + 'SubmittedCount', submitted_count)
        self.add_result(results, prefix + 'TotalLag', total_lag)
    
    def calculate_cif_indicators(self, results, query_set):
        self.calculate_form_indicators(results, query_set, 'cif')
    
    def calculate_vdf_indicators(self, results, query_set):
        self.calculate_form_indicators(results, query_set, 'vdf')
    
    def process_photos(self, results, station_list, start_date, end_date):
        photos_uploaded = 0
        photo_lag_total = 0
        
        class_cache = {
                'form':{},
                'IRF': {},
                'interceptee':{}
            }
        
        for entry in os.scandir(settings.PUBLIC_ROOT + '/interceptee_photos/'):
            the_station = None
            for station in station_list:
                if entry.name.startswith(station.station_code):
                    the_station = station
                    break
            
            if the_station is None:
                # station code prefix is not one of the stations we are interested in
                continue
            
            time_zone = pytz.timezone(the_station.time_zone)
            stat_object = entry.stat ( )
            modification_time = datetime.datetime.fromtimestamp(stat_object.st_mtime)
            local_date = instance.astimezone(time_zone)
            if local_date < start_date or local_date > end_date:
                # file modification date is not in our time range
                continue
            
            parts = entry.name.split('_')
            
            irf_class = self.get_class('IRF', the_station)
            if irf_class is None:
                continue
            
            irf = irf_class.objects.get('irf_number',parts[0])
            if irf is None:
                continue
            
            interceptee_class = self.get_class('Interceptee', the_station)
            if interceptee_class is None:
                continue
            
            interceptees = interceptee_class.objects.filter(interception_record=irf)
            found = False
            for interceptee in interceptees:
                if entry.name in interceptee.photo:
                    photos_uploaded += 1
                    if self.date_present(irf.logbook_information_complete):
                        base_date = irf.logbook_information_complete
                    elif self.date_present(irf.logbook_received):
                        base_date = irf.logbook_received
                    else:
                        base_date = irf.date_time_entered_into_system.date()
                    
                    photo_lag_total += self.work_days(base_date, local_date)
                    break
            
        self.add_result(results, 'photosUploaded', photos_uploaded)
        self.add_result(results, 'photosLagTotal', photo_lag_total)
            
            
            
                