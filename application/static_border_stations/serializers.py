
from rest_framework import serializers
from static_border_stations.models import Staff, CommitteeMember, Location


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Staff


class CommitteeMemberSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = CommitteeMember


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Location
