
from rest_framework import serializers
from static_border_stations.models import Staff, CommitteeMember, Location
from dataentry.models import UserLocationPermission
from rest_framework.exceptions import APIException
from django.utils.encoding import force_text
from rest_framework import status

class CustomValidation(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A server error occurred'
    
    def __init__(self, detail, field, status_code):
        if status_code is not None:
            self.status_code = status_code
            if detail is not None:
                self.detail = {field: [force_text(detail), ]}
            else:
                self.detail = {'detail': force_text(self.default_detail)}

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Staff

    def create(self, validated_data):
        border_station = validated_data.get('border_station', None)
        if border_station is not None and not UserLocationPermission.has_session_permission(self.context['request'], 'STATIONS', 'ADD', border_station.operating_country.id, border_station.id):
            raise CustomValidation('You are not authorized to add staff in ' + border_station.station_name, 'border_station', status.HTTP_401_UNAUTHORIZED)
        return Staff.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        border_station = validated_data.get('border_station', instance.border_station)
        if border_station is not None and not UserLocationPermission.has_session_permission(self.context['request'], 'STATIONS', 'EDIT', border_station.operating_country.id, border_station.id):
            raise CustomValidation('You are not authorized to edit staff in ' + border_station.station_name, 'border_station', status.HTTP_401_UNAUTHORIZED)
        return super(StaffSerializer,self).update(instance, validated_data)

class CommitteeMemberSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = CommitteeMember

    def create(self, validated_data):
        border_station = validated_data.get('border_station', None)
        if (border_station is not None and border_station.operating_country is not None and 
                not UserLocationPermission.has_session_permission(self.context['request'], 'STATIONS', 'ADD', border_station.operating_country.id, border_station.id)):
            raise CustomValidation('You are not authorized to add committee members in ' + border_station.station_name, 'border_station', status.HTTP_401_UNAUTHORIZED)
        return CommitteeMember.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        border_station = validated_data.get('border_station', instance.border_station)
        if (border_station is not None and border_station.operating_country is not None and
                not UserLocationPermission.has_session_permission(self.context['request'], 'STATIONS', 'EDIT', border_station.operating_country.id, border_station.id)):
            raise CustomValidation('You are not authorized to edit committee members in ' + border_station.station_name, 'border_station', status.HTTP_401_UNAUTHORIZED)
        return super(CommitteeMemberSerializer,self).update(instance, validated_data)

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Location

    def create(self, validated_data):
        border_station = validated_data.get('border_station', None)
        if border_station is not None and not UserLocationPermission.has_session_permission(self.context['request'], 'STATIONS', 'ADD', border_station.operating_country.id, border_station.id):
            raise CustomValidation('You are not authorized to add locations in ' + border_station.station_name, 'border_station', status.HTTP_401_UNAUTHORIZED)
        return Location.objects.create(**validated_data)
        
    def update(self, instance, validated_data):
        border_station = validated_data.get('border_station', instance.border_station)
        if border_station is not None and not UserLocationPermission.has_session_permission(self.context['request'], 'STATIONS', 'EDIT', border_station.operating_country.id, border_station.id):
            raise CustomValidation('You are not authorized to edit locations in ' + border_station.station_name, 'border_station', status.HTTP_401_UNAUTHORIZED)
        return super(LocationSerializer,self).update(instance, validated_data)