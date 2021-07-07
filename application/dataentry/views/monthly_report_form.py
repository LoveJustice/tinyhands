import pytz

from rest_framework import serializers
from rest_framework import filters as fs
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response

from dataentry.serialize_form import FormDataSerializer
from .base_form import BaseFormViewSet, BorderStationOverviewSerializer

from dataentry.form_data import Form, FormData
from dataentry.models import BorderStation, Country, MonthlyReport

class MonthlyReportListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    year = serializers.IntegerField()
    month = serializers.IntegerField()
    date_time_entered_into_system = serializers.SerializerMethodField(read_only=True)
    date_time_last_updated = serializers.SerializerMethodField(read_only=True)
    station = BorderStationOverviewSerializer()
    form_name = serializers.SerializerMethodField(read_only=True)
    
    perm_group_name = 'MONTHLY_REPORT'
    
    def adjust_date_time_for_tz(self, date_time, tz_name):
        tz = pytz.timezone(tz_name)
        date_time = date_time.astimezone(tz)
        date_time = date_time.replace(microsecond=0)
        date_time = date_time.replace(tzinfo=None)
        return str(date_time)
    
    def get_date_time_entered_into_system(self, obj):
        return self.adjust_date_time_for_tz (obj.date_time_entered_into_system, obj.station.time_zone)[0:10]
    
    def get_date_time_last_updated(self, obj):
        return self.adjust_date_time_for_tz (obj.date_time_last_updated, obj.station.time_zone)
    
    def get_form_name(self, obj):
        forms = Form.objects.filter(form_type__name='MONTHLY_REPORT', stations__id=obj.station.id)
        if len(forms) > 0:
            return forms[0].form_name
        else:
            return None
    
class MonthlyReportFormViewSet(BaseFormViewSet):
    parser_classes = (MultiPartParser,FormParser,JSONParser)
    permission_classes = (IsAuthenticated, )
    serializer_class = MonthlyReportListSerializer
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ('station__station_code',)
    ordering_fields = [
        'year', 'month',
        'date_time_entered_into_system',
        'date_time_last_updated']
    ordering = ('-year','-month')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MonthlyReportListSerializer
        else:
            return FormDataSerializer
    
    def get_serializer_context(self): 
        return self.serializer_context
    
    def get_perm_group_name(self):
        return 'MONTHLY_REPORT'
    
    def get_form_type_name(self):
        return 'MONTHLY_REPORT'
    
    def get_element_paths(self):
        return [
            {
                'element':'scanned',
                'path':'mrf_attachments/'
            }
        ]
    
    def get_list_field_names(self):
        return ['id', 'year', 'month', 'form_entered_by',
                'station', 'date_time_entered_into_system',
                'date_time_last_updated']
        
    def get_empty_queryset(self):
        return MonthlyReport.objects.none()
    
    def filter_key(self, queryset, search):
        return queryset.filter(station__station_code__contains=search)
    
    def compute_total(self, totals, field_name, value):
        if field_name in totals:
            totals[field_name] = totals[field_name] + value
        else:
            totals[field_name] = value
    
    def summary(self, request, country_id, year, month):
        country = Country.objects.get(id=country_id)
        point_heading = {
                "govern_points":"Governance",
                "logistics_points":"Logistics & Registration",
                "human_points":"Human Resources",
                "awareness_points":"Awareness",
                "security_points":"Security",
                "accounting_points":"Accounting",
                "engagement_points":"Victim Engagement",
                "records_points":"Records",
                "aftercare_points":"Aftercare",
                "paralegal_points":"Paralegal",
            }
        
        options = country.options
        if options is None or 'monthly_report_sections' not in options:
            # If sections are not specified in country table, then assume all sections
            report_sections = point_heading.keys()
        else:
            report_sections = options['monthly_report_sections']

        stations = BorderStation.objects.filter(operating_country=country)
        reports = MonthlyReport.objects.filter(year=year, month=month, station__in=stations).order_by("station__station_code")
        results = {
                "headings":["Station"],
                "reports":[],
                "averages":["Average"]
            }
        
        for field_name in report_sections:
            results["headings"].append(point_heading[field_name])
        results["headings"].append("Average")
        
        section_totals = {}
        report_count = 0
        for report in reports:
            report_count += 1
            report_data = [report.station.station_code]
            
            total = 0
            count = 0
            for field_name in report_sections:
                heading = point_heading[field_name]
                val = getattr(report, field_name)
                report_data.append(val)
                self.compute_total(section_totals, heading, val)
                count += 1
                total += val
            
            if count  > 0:
                val = round(total/count,1)
                report_data.append(val)
                self.compute_total(section_totals, 'Average', val)
            else:
                report_data.append('NA')
                self.compute_total(section_totals, 'Average', 0)
            results["reports"].append(report_data)
        
        if report_count> 0:
            for heading in results["headings"]:
                if heading == 'Station':
                    continue
                results["averages"].append(round(section_totals[heading]/report_count,1))
            
        return Response (results)
            

