
from rest_framework import serializers
from static_border_stations.models import Staff, CommitteeMember, Location, WorksOnProject


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = [field.name for field in model._meta.fields] # all the model fields
        fields = fields + ['works_on']
        
    works_on = serializers.SerializerMethodField(read_only=True)
    
    def get_works_on (self, obj):
        rtn = []
        works_on_list = WorksOnProject.objects.filter(staff=obj)
        for works_on in works_on_list:
            rtn.append({
                'id': works_on.id,
                'financial': {
                    'project_id': obj.border_station.id,
                    'project_name': obj.border_station.station_name,
                    'project_code': obj.border_station.station_code
                },
                'works_on':{
                    'project_id': works_on.border_station.id,
                    'project_name': works_on.border_station.station_name,
                    'project_code': works_on.border_station.station_code
                },
                'percent':works_on.work_percent})
        return rtn


class CommitteeMemberSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = CommitteeMember


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Location
