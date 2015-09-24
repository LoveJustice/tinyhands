from rest_framework import serializers

from dataentry.models import District, VDC, BorderStation


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District


class VDCSerializer(serializers.ModelSerializer):
    class Meta:
        model = VDC
        exclude = ['district']


class BorderStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BorderStation