from rest_framework import serializers
from events.models import Event

class EventsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
