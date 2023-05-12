
from rest_framework import serializers
from dataentry.models import BorderStation
from static_border_stations.models import Staff, StaffProject, CommitteeMember, Location, WorksOnProject

class StaffProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffProject
        fields = [field.name for field in model._meta.fields] # all the model fields

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = [field.name for field in model._meta.fields] # all the model fields
        fields = fields + ['works_on', 'staffproject_set']
    
    works_on = serializers.SerializerMethodField(read_only=True)
    staffproject_set = StaffProjectSerializer(many=True)
    
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
    
    def to_internal_value(self, data):
        print('Enter StaffSerializer.to_internal_value', data)
        
        if 'staffproject_set' in data:
            staff_project = data['staffproject_set']
            data['staffproject_set'] = []
        else:
            data['staffproject_set'] = []
            staff_project = []
        print('Enter StaffSerializer.to_internal_value before super')
        validated = super().to_internal_value(data)
        print('Enter StaffSerializer.to_internal_value after super')
        validated['staffproject_set'] = staff_project
        print('Exit StaffSerializer.to_internal_value', validated)
        return validated
    
    def update(self, instance, validated_data):
        print('Enter StaffSerializer.update', validated_data)
        staff_project = validated_data['staffproject_set']
        del validated_data['staffproject_set']
        obj = super().update(instance, validated_data)
        to_delete = []
        staff_project_list = StaffProject.objects.filter(staff=obj)
        for existing in staff_project_list:
            found = False
            for new_data in staff_project:
                if existing.id == new_data['id']:
                    found = True
                    existing.receives_money_distribution_form = new_data['receives_money_distribution_form']
                    existing.coordinator = new_data['coordinator']
                    existing.save()
                    break
            if not found:
                to_delete.append(existing)

        for existing in to_delete:
            existing.delete()

        for new_data in staff_project:
            if new_data['id'] is None:
                entry = StaffProject()
                entry.staff = instance
                entry.border_station = BorderStation.objects.get(id=new_data['border_station'])
                entry.receives_money_distribution_form = new_data['receives_money_distribution_form']
                entry.coordinator = new_data['coordinator']
                entry.save()
        
        print('Exit StaffSerializer.update')
        return obj

    def create(self, validated_data):
        print('Enter StaffSerializer.create', validated_data)
        staff_project = validated_data['staffproject_set']
        del validated_data['staffproject_set']
        obj = super().create(validated_data)
        obj.save()
        for new_data in staff_project:
            entry = StaffProject()
            entry.staff = obj
            entry.border_station = BorderStation.objects.get(id=new_data['border_station'])
            entry.receives_money_distribution_form = new_data['receives_money_distribution_form']
            entry.coordinator = new_data['coordinator']
            entry.save()
        
        print('Exit StaffSerializer.create')
        return obj



class CommitteeMemberSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = CommitteeMember


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Location
