import datetime
from itertools import chain

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from events.helpers import get_repeated_events, event_list, dashboard_event_list
from events.models import Event
from events.serializers import EventsSerializer


# Rest Api Views
class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventsSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False)
    def list_all(self, request):
        events = Event.objects.all()
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def calendar_feed(self, request):
        try:
            start = request.query_params.get('start', '')
            end = request.query_params.get('end', '')
            start_date = datetime.datetime.strptime(start, "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(end, "%Y-%m-%d").date()
            if start_date > end_date:
                return Response("Start date is later than end date", status=status.HTTP_400_BAD_REQUEST)
            querydict = {}
            if start_date:
                querydict['start_date__gte'] = start_date
            if end_date:
                querydict['start_date__lte'] = end_date
            querydict['is_repeat'] = False

            event_data = query_events_for_feed(querydict, start_date, end_date)
            events = event_list(event_data)
            return Response(events)
        except ValueError:
            return Response("Date does not match format YYYY-MM-DD", status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False)
    def dashboard_feed(self, request):
        start_date = datetime.date.today()
        end_date = start_date + datetime.timedelta(days=7)
        querydict = {
            'start_date__gte': start_date,
            'start_date__lte': end_date,
            'is_repeat': False
        }

        event_data = query_events_for_feed(querydict, start_date, end_date)
        events = dashboard_event_list(event_data)
        return Response(events)


def query_events_for_feed(querydict, start_date, end_date):
    repeated_events = Event.objects.filter(is_repeat=True)
    non_repeated_events = Event.objects.filter(**querydict)

    temp_events = get_repeated_events(repeated_events, start_date, end_date)
    result_list = list(chain(temp_events, non_repeated_events))
    return result_list
