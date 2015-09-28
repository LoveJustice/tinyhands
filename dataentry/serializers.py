from rest_framework import serializers

from dataentry.models import District, VDC


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District


class VDCSerializer(serializers.ModelSerializer):
    cannonical_name = serializers.StringRelatedField()
    # district = serializers.PrimaryKeyRelatedField(queryset=District.objects.all())
    district = DistrictSerializer()

    class Meta:
        model = VDC
        depth = 1

    def create(self, validated_data):
        found_district = District.objects.get(pk=self.context['request'].data['district']['id'])
        validated_data['district'] = found_district
        return VDC.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.district = District.objects.get(pk=self.context['request'].data['district']['id'])
        instance.name = validated_data.get('name', instance.name)
        instance.cannonical_name = validated_data.get('cannonical_name', instance.cannonical_name)
        instance.latitude = validated_data.get('latitude', instance.latitude)
        instance.longitude = validated_data.get('longitude', instance.longitude)
        instance.verified = validated_data.get('verified', instance.verified)
        return instance
