from rest_framework import serializers
from events.models import Event


class EventsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event

    def validate(self, data):
        if data['is_repeat'] and not data['repetition']:
            raise serializers.ValidationError('Repetition is required if event is repeated.')

        start_date = data['start_date']
        end_date = data['end_date']
        start_time = data['start_time']
        end_time = data['end_time']
        ends = data['ends']
        if start_date and end_date:
            if start_date > end_date:
                raise serializers.ValidationError('Start date is not allowed to be greater than end date.')
            if start_date == end_date:
                if start_time > end_time:
                    raise serializers.ValidationError('Start time must less than end time for same day.')
        if ends and ends <= start_date:
            raise serializers.ValidationError('Events repetition ends must be greater than first event end date.')
        return data
