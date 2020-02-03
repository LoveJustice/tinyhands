from rest_framework import serializers

from help.models import Video

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Video