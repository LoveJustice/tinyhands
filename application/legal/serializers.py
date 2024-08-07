from rest_framework import serializers
from dataentry.models import Form, Incident, Suspect, VdfCommon
from legal.models import CourtCase, LegalCharge, LegalChargeSuspect, LegalChargeSuspectCharge, LegalChargeVictim, LegalChargeCountrySpecific
from dataentry.serializers import PersonSerializer

class LegalChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalCharge
        fields = [field.name for field in model._meta.fields] # all the model fields
        fields = fields + ['form_name','incident_number', 'country_id','station_code','number_victims','number_suspects','number_arrests',
                           'number_cases', 'number_convictions', 'charges', 'last_timeline_date']
    
    form_name = serializers.SerializerMethodField(read_only=True)
    incident_number = serializers.SerializerMethodField(read_only=True)
    country_id = serializers.SerializerMethodField(read_only=True)
    station_code = serializers.SerializerMethodField(read_only=True)
    number_victims = serializers.SerializerMethodField(read_only=True)
    number_suspects = serializers.SerializerMethodField(read_only=True)
    number_arrests = serializers.SerializerMethodField(read_only=True)
    number_cases = serializers.SerializerMethodField(read_only=True)
    number_convictions = serializers.SerializerMethodField(read_only=True)
    charges = serializers.SerializerMethodField(read_only=True)
    last_timeline_date = serializers.SerializerMethodField(read_only=True)
    
    def get_form_name(self, obj):
        forms = Form.objects.filter(form_type__name='LEGAL_CASE', stations__id=obj.station.id)
        if len(forms) > 0:
            return forms[0].form_name
        else:
            return None
    
    def get_incident_number(self, obj):
        return obj.incident.incident_number
    
    def get_country_id(self, obj):
        return obj.station.operating_country.id
    
    def get_station_code(self, obj):
        return obj.station.station_code
    
    def get_number_victims(self, obj):
        return LegalChargeVictim.objects.filter(legal_charge=obj).count()
    
    def get_number_suspects(self, obj):
        return LegalChargeSuspect.objects.filter(legal_charge=obj).count()
    
    def get_number_arrests(self, obj):
        return LegalChargeSuspect.objects.filter(legal_charge=obj, arrested="Yes").count()
    
    def get_number_cases(self, obj):
        return CourtCase.objects.filter(legal_charge=obj).count()
    
    def get_charges(self, obj):
        charges = ''
        sep = ''
        cases = CourtCase.objects.filter(legal_charge=obj)
        for case in cases:
            if case.charges is not None:
                charges += sep + case.charges
                sep = ', '
        
        return charges
    
    def get_number_convictions(self, obj):
        return LegalChargeSuspectCharge.objects.filter(legal_charge=obj, verdict='Conviction').count()
    
    def get_last_timeline_date(self, obj):
        result = None
        timelines = obj.legalchargetimeline_set.filter(date_removed__isnull=True).order_by('-comment_date')
        if len(timelines) > 0:
            result = timelines[0].comment_date
        return result

class LegalChargeIncidentSfSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suspect
        fields = ['id','sf_number', 'merged_person']
        
    merged_person = PersonSerializer()

class LegalChargeIncidentPvfSerializer(serializers.ModelSerializer):
    class Meta:
        model = VdfCommon
        fields = ['id','vdf_number', 'victim']
    
    victim = PersonSerializer()

class LegalChargeIncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = [field.name for field in model._meta.fields] # all the model fields
        fields = fields + ['sfs','pvfs']
    
    sfs = serializers.SerializerMethodField(read_only=True)
    pvfs = serializers.SerializerMethodField(read_only=True)
    
    def get_sfs(self, obj):
        sfs = Suspect.objects.filter(incidents=obj)
        serializer = LegalChargeIncidentSfSerializer(sfs, many=True)
        return serializer.data
    
    def get_pvfs(self, obj):
        filtered_pvfs = []
        pvfs = VdfCommon.objects.filter(vdf_number__startswith=obj.incident_number)
        for pvf in pvfs:
            station = obj.station
            form_number = pvf.vdf_number
            base_number = form_number
            for idx in range(len(station.station_code), len(form_number)):
                if (form_number[idx] < '0' or form_number[idx] > '9') and form_number[idx] != '_':
                    base_number = form_number[:idx]
                    break
            if base_number == obj.incident_number:
                filtered_pvfs.append(pvf)
                
        serializer = LegalChargeIncidentPvfSerializer(filtered_pvfs, many=True)
        return serializer.data

class LegalChargeCountrySpecificSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalChargeCountrySpecific
        fields = [field.name for field in model._meta.fields] # all the model fields
    
    
    