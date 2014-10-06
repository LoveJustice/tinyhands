from rest_framework import serializers

from dataentry.models import District, VDC

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District


class VDCSerializer(serializers.ModelSerializer):
	class Meta:
		model = VDC
		exlude = ['district']