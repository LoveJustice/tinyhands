import datetime
import json

from rest_framework import serializers

from dataentry.models import Address1, Address2, Country, SiteSettings, InterceptionRecord, VictimInterview, BorderStation, Person, Interceptee, InterceptionAlert
from static_border_stations.serializers import LocationSerializer

from helpers import related_items_helper



class Address1Serializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Address1


class Address1RelatedItemsSerializer(Address1Serializer):
    related_items = serializers.SerializerMethodField()
    get_related_items = related_items_helper

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Country

class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = SiteSettings


class CanonicalNameSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'name']
        model = Address2


class Address2Serializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Address2
        depth = 1

    def create(self, validated_data):
        found_address1 = Address1.objects.get(pk=self.context['request'].data['address1']['id'])
        if self.context['request'].data['canonical_name']['id'] == -1:
            found_address2 = None
        else:
            found_address2 = Address2.objects.get(pk=self.context['request'].data['canonical_name']['id'])
        validated_data['address1'] = found_address1
        validated_data['canonical_name'] = found_address2
        return Address2.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.address1 = Address1.objects.get(pk=self.context['request'].data['address1']['id'])
        instance.name = validated_data.get('name', instance.name)
        if self.context['request'].data['canonical_name']['id'] == -1:
            instance.canonical_name = None
        else:
            instance.canonical_name = Address2.objects.get(pk=self.context['request'].data['canonical_name']['id'])
        instance.latitude = validated_data.get('latitude', instance.latitude)
        instance.longitude = validated_data.get('longitude', instance.longitude)
        instance.level = validated_data.get('level', instance.level)
        instance.verified = validated_data.get('verified', instance.verified)
        instance.save()
        return instance

    canonical_name = CanonicalNameSerializer(required=False)
    address1 = Address1Serializer()


class Address2RelatedItemsSerializer(Address2Serializer):
    related_items = serializers.SerializerMethodField()
    get_related_items = related_items_helper


class BorderStationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = BorderStation

    number_of_interceptions = serializers.SerializerMethodField(read_only=True)
    number_of_staff = serializers.SerializerMethodField(read_only=True)
    ytd_interceptions = serializers.SerializerMethodField(read_only=True)
    location_set = LocationSerializer(many=True, read_only=True)

    def get_number_of_interceptions(self, obj):
        return Interceptee.objects.filter(interception_record__irf_number__startswith=obj.station_code, kind='v').count()

    def get_number_of_staff(self, obj):
        return obj.staff_set.all().count()

    def get_ytd_interceptions(self, obj):
        return Interceptee.objects.filter(interception_record__irf_number__startswith=obj.station_code, kind='v', interception_record__date_time_of_interception__year=datetime.date.today().year).count()


class InterceptionRecordListSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterceptionRecord
        fields = [
            'view_url',
            'edit_url',
            'delete_url',
            'id',
            'irf_number',
            'staff_name',
            'number_of_victims',
            'number_of_traffickers',
            'date_time_of_interception',
            'date_time_entered_into_system',
            'date_time_last_updated'
        ]

    view_url = serializers.HyperlinkedIdentityField(
        view_name='interceptionrecord_detail',
        read_only=True
    )
    edit_url = serializers.HyperlinkedIdentityField(
        view_name='interceptionrecord_update',
        read_only=True
    )
    delete_url = serializers.HyperlinkedIdentityField(
        view_name='InterceptionRecordDetail',
        read_only=True
    )


class InterceptionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = InterceptionRecord

    def validate(self, data):
        validation_response = {}
        errors = self.check_for_errors(data)
        warnings = self.check_for_warnings(data)
        if len(errors) > 0:
            validation_response['errors'] = errors
        if len(warnings) > 0:
            validation_response['warnings'] = warnings
        if len(warnings) > 0 or len(errors) > 0:
            raise serializers.ValidationError(validation_response)
        return data

    def check_for_errors(self, data):  # For Error validation
        errors = []
        errors += self.check_for_none_checked(data)
        if data['contact_noticed'] == False and data['staff_noticed'] == False:
            errors.append({'contact_noticed': 'Either Contact (6.0) or Staff (7.0) must be chosen for how interception was made.'})
        return errors

    def check_for_none_checked(self, data):  # For Error validation
        errors = []
        has_none_checked = True
        for field in data:
            if isinstance(data[field], bool) and data[field] == True:
                has_none_checked = False
        if has_none_checked:
            errors.append({'no_checkboxes_checked': 'At least one box must be checked on the first page.'})
        return errors

    def check_for_red_flags(self, data):  # For Warning validation
        warnings = []
        any_red_flags = False
        for field in InterceptionRecord._meta.fields:
            try:
                if field.weight is not None:
                    if data[field.name]:
                        any_red_flags = True
            except:
                pass
        if not any_red_flags:
            warnings.append({'red_flags': 'No red flags are checked.'})
        return warnings

    def check_for_warnings(self, data):  # For Warning validation
        warnings = []
        warnings += self.check_for_red_flags(data)
        warnings += self.check_procedure(data)
        warnings += self.check_type(data)
        if not data['has_signature']:
            warnings.append({'has_signature': 'Form should be signed, though not required.'})
        return warnings

    def check_procedure(self, data):  # For Warning validation
        warnings = []
        if not data['call_thn_to_cross_check']:
            warnings.append({'call_thn_to_cross_check': 'Procedure not followed.'})
        if not data['call_subcommittee_chair']:
            warnings.append({'call_subcommittee_chair': 'Procedure not followed.'})
        if not data['scan_and_submit_same_day']:
            warnings.append({'scan_and_submit_same_day': 'Procedure not followed.'})
        return warnings

    def check_type(self, data):  # For Warning validation
        warnings = []
        type_is_set = False
        for field in InterceptionRecord._meta.fields:
            try:
                if field.name:
                    if 'type' in field.name and data[field.name]:
                        type_is_set = True
            except:
                pass
        if not type_is_set:
            warnings.append({'interception_type': 'Field should be included, though not required.'})
        return warnings


class VictimInterviewListSerializer(serializers.ModelSerializer):
    class Meta:
        model = VictimInterview
        fields = [
            'view_url',
            'edit_url',
            'delete_url',
            'id',
            'vif_number',
            'interviewer',
            'number_of_victims',
            'number_of_traffickers',
            'date',
            'date_time_entered_into_system',
            'date_time_last_updated'
        ]

    view_url = serializers.HyperlinkedIdentityField(
        view_name='victiminterview_detail',
        read_only=True
    )
    edit_url = serializers.HyperlinkedIdentityField(
        view_name='victiminterview_update',
        read_only=True
    )
    delete_url = serializers.HyperlinkedIdentityField(
        view_name='VictimInterviewDetail',
        read_only=True
    )


class VictimInterviewPersonBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = VictimInterview
        exclude = []


class VictimInterviewLocationBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = VictimInterview
        exclude = []


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = [
            'full_name',
            'gender',
            'age',
            'address1',
            'address2',
            'phone_contact',
        ]

class IDManagementSerializer(serializers.ModelSerializer):
    aliases = serializers.CharField(source='get_aliases', read_only=True)
    form_type = serializers.CharField(source='get_form_type', read_only=True)
    form_number = serializers.CharField(source='get_form_number', read_only=True)
    form_date = serializers.CharField(source='get_form_date', read_only=True)
    form_photo = serializers.ImageField(source='get_form_photo', use_url=True, read_only=True)
    form_kind = serializers.CharField(source='get_form_kind', read_only=True)
    address1 = Address1Serializer(read_only=True)
    address2 = Address2Serializer(read_only=True)

    class Meta:
        model = Person
        fields = [
            'id',
            'full_name',
            'gender',
            'age',
            'address1',
            'address2',
            'phone_contact',
            'alias_group',
            'aliases',
            'form_type',
            'form_number',
            'form_date',
            'form_photo',
            'form_kind',
        ]

class PersonFormsSerializer(serializers.Serializer):
    number = serializers.CharField()
    date = serializers.CharField()

class VictimInterviewSerializer(serializers.ModelSerializer):
    victim_guardian_address1 = Address1Serializer(read_only=True)
    victim_guardian_address2 = Address2Serializer(read_only=True)
    victim = PersonSerializer(read_only=True)

    class Meta:
        model = VictimInterview
        read_only_fields = ('person_boxes', 'location_boxes')
        exclude = []
        depth = 1


class IntercepteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interceptee
        fields = [
            'photo',
            'id',
            'interception_record',
            'kind',
            'relation_to',
            'person',
        ]
    person = PersonSerializer()
    

class InterceptionAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterceptionAlert
        fields = ['json']

    def to_representation(self, obj):
        return json.loads(obj.json)