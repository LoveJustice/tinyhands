from rest_framework import serializers
from .models import MatchingData, MatchingPerson, AnalyzedPerson

# class FaceMatchingSerializer(serializers.ModelSerializer):
#     class Meta:
#         # model = FaceEncoding
#         fields = '__all__'
        
class AnalyzedPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyzedPerson
        fields = ['face_photo', 'full_photo', 'face_analysis']
        
    
class MatchingPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchingPerson
        fields = ['full_name', 'person_id', 'gender', 'role', 'face_photo', 'full_photo', 'irf_number', 'nationality', 'age_at_interception', 'date_of_interception', 'face_analysis', 'face_distance']

class MatchingDataSerializer(serializers.ModelSerializer):
    analyzedPerson = AnalyzedPersonSerializer()
    matchingPersons = MatchingPersonSerializer(many=True)

    class Meta:
        model = MatchingData
        fields = ['analyzedPerson', 'matchingPersons']