from django.core.urlresolvers import reverse
from rest_framework import serializers

from dataentry.models import District, VDC, InterceptionRecord, VictimInterview


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District


class CannonicalNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = VDC
        fields = ['id', 'name']


class VDCSerializer(serializers.ModelSerializer):
    class Meta:
        model = VDC
        depth = 1

    def create(self, validated_data):
        found_district = District.objects.get(pk=self.context['request'].data['district']['id'])
        if self.context['request'].data['cannonical_name']['id'] == -1:
            found_vdc = None
        else:
            found_vdc = VDC.objects.get(pk=self.context['request'].data['cannonical_name']['id'])
        validated_data['district'] = found_district
        validated_data['cannonical_name'] = found_vdc
        return VDC.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.district = District.objects.get(pk=self.context['request'].data['district']['id'])
        instance.name = validated_data.get('name', instance.name)
        if self.context['request'].data['cannonical_name']['id'] == -1:
            instance.cannonical_name = None
        else:
            instance.cannonical_name = VDC.objects.get(pk=self.context['request'].data['cannonical_name']['id'])
        instance.latitude = validated_data.get('latitude', instance.latitude)
        instance.longitude = validated_data.get('longitude', instance.longitude)
        instance.verified = validated_data.get('verified', instance.verified)
        instance.save()
        return instance

    cannonical_name = CannonicalNameSerializer()
    district = DistrictSerializer()


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

