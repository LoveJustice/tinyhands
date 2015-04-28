from rest_framework import serializers
from static_border_stations.models import Staff


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff