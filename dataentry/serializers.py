from rest_framework import serializers

from dataentry.models import District, VDC


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District


class CannonicalNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = VDC
        fields = ['id','name']

class VDCSerializer(serializers.ModelSerializer):
    class Meta:
        model = VDC
        depth = 1

    def create(self, validated_data):
        found_district = District.objects.get(pk=self.context['request'].data['district']['id'])
        found_vdc = VDC.objects.get(pk=self.context['request'].data['cannonical_name']['id'])
        validated_data['district'] = found_district
        validated_data['cannonical_name'] = found_vdc
        return VDC.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.district = District.objects.get(pk=self.context['request'].data['district']['id'])
        instance.name = validated_data.get('name', instance.name)
        instance.cannonical_name = VDC.objects.get(pk=self.context['request'].data['cannonical_name']['id'])
        instance.latitude = validated_data.get('latitude', instance.latitude)
        instance.longitude = validated_data.get('longitude', instance.longitude)
        instance.verified = validated_data.get('verified', instance.verified)
        instance.save()
        return instance

    cannonical_name = CannonicalNameSerializer()
    district = DistrictSerializer()