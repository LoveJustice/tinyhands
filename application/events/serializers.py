from rest_framework import serializers
from events.models import Event

class EventsSerializer(serializers.ModelSerializer):
    has_been_activated = serializers.BooleanField(source='has_usable_password',read_only=True)

    class Meta:
        model = Event
