from rest_framework import serializers

from dataentry.models import Address1, Address2, InterceptionRecord, VictimInterview, BorderStation


class Address1Serializer(serializers.ModelSerializer):
    class Meta:
        model = Address1


class CanonicalNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address2
        fields = ['id', 'name']


class Address2Serializer(serializers.ModelSerializer):
    class Meta:
        model = Address2
        depth = 1

    def create(self, validated_data):
        found_address1 = Address1.objects.get(pk=self.context['request'].data['address1']['id'])
        found_address2 = None
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
        instance.verified = validated_data.get('verified', instance.verified)
        instance.save()
        return instance

    canonical_name = CanonicalNameSerializer()
    address1 = Address1Serializer()


class BorderStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BorderStation

    def validate(self, data):
        if data['has_signature'] is not True:
            raise serializers.ValidationError({'has_signature': 'Form should be signed, though not required.'})
        return data


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

    def check_for_errors(self, data): # For validation
        errors = []
        return errors

    def check_for_red_flags(self, data): # For validation
        any_red_flags = False
        for field in InterceptionRecord._meta.fields:
            try:
                if field.weight:
                    if data[field.name] == True:
                        any_red_flags = True
            except:
                pass
        if any_red_flags == False:
            return [{'red_flags': 'No red flags are checked.'}]
        return []

    def check_for_warnings(self, data): # For validation
        warnings = []
        warnings += self.check_for_red_flags(data)
        warnings += self.check_procedure(data)
        warnings += self.check_type(data)
        if data['has_signature'] == False:
            warnings.append({'has_signature': 'Form should be signed, though not required.'})
        return warnings


    def check_procedure(self, data): # For validation
        warnings = []
        if data['call_thn_to_cross_check'] == False:
            warnings.append({'call_thn_to_cross_check': 'Procedure not followed.'})
        if data['call_subcommittee_chair'] == False:
            warnings.append({'call_subcommittee_chair': 'Procedure not followed.'})
        if data['scan_and_submit_same_day'] == False:
            warnings.append({'scan_and_submit_same_day': 'Procedure not followed.'})
        return warnings

    def check_type(self, data): # For validation
        type_is_set = False
        for field in InterceptionRecord._meta.fields:
            try:
                if field.name:
                    if 'type' in field.name and data[field.name] == True:
                        type_is_set = True
            except:
                pass
        if type_is_set == False:
            return [{'interception_type': 'Field should be included, though not required.'}]
        return []




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
