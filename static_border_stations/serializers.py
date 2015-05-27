from rest_framework import serializers
from static_border_stations.models import Staff, CommitteeMember


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff


class CommitteeMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommitteeMember