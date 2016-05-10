import datetime
import json
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.views.generic import CreateView, ListView, TemplateView, DeleteView, UpdateView
from events.forms import EventForm
from events.helpers import get_repeated, event_list, dashboard_event_list
from events.models import Event
from itertools import chain

from rest_framework import status
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from events.models import Event
from events.serializers import EventsSerializer

class EventCreateView(SuccessMessageMixin, CreateView):
    template_name = 'events/event_form.html'
    form_class = EventForm
    success_url = '/events/calendar/'

    def form_valid(self, form):
        start_date = form.cleaned_data.get('start_date', None)
        start_time = form.cleaned_data.get('start_time', None)
        form.instance.end_date = start_date
        form.instance.end_time = (datetime.datetime.combine(datetime.date.today(), start_time) + datetime.timedelta(hours=1)).time()
        return super(EventCreateView, self).form_valid(form)

    def get_success_message(self, cleaned_data):
        title = cleaned_data.get('title', '')
        message = '" {} " event is saved successfully.'.format(title)
        return message


class EventListView(ListView):
    template_name = 'events/event_list.html'
    model = Event


class EventCalendarView(TemplateView):
    template_name = 'events/event_calendar.html'


class EventDeleteView(DeleteView):
    model = Event
    success_url = '/events/list/'
    template_name = 'events/event_delete.html'
    success_message = "event is deleted successfully."

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        success_message = '" {} " {}'.format(obj.title, self.success_message)
        messages.success(self.request, success_message)
        return super(EventDeleteView, self).delete(request, *args, **kwargs)


class EventUpdateView(SuccessMessageMixin, UpdateView):
    model = Event
    template_name = 'events/event_form.html'
    form_class = EventForm
    success_url = '/events/list/'

    def get_success_message(self, cleaned_data):
        title = cleaned_data.get('title', '')
        message = '" {} " event is updated successfully.'.format(title)
        return message


class EventJson(ListView):
    model = Event

    def get_queryset(self, queryset=None):
        dashboard = self.kwargs.get('dashboard', '')
        listing_event = dashboard_event_list if dashboard else event_list
        if dashboard:
            start_date = datetime.date.today()
            end_date = start_date + datetime.timedelta(days=7)
            querydict = {
                'start_date__gte': start_date,
                'start_date__lte': end_date,
                'is_repeat': False
            }
        else:
            start = self.request.GET.get('start', '')
            end = self.request.GET.get('end', '')
            start_date = datetime.datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.datetime.strptime(end, "%Y-%m-%d")
            querydict = {}
            if start_date:
                querydict['start_date__gte'] = start_date
            if end_date:
                querydict['start_date__lte'] = end_date
            querydict['is_repeat'] = False

        qs_repeat = self.model.objects.filter(is_repeat=True)
        qs_non_repeat = self.model.objects.filter(**querydict)

        temp_events = get_repeated(qs_repeat, start_date, end_date)
        result_list = list(chain(temp_events, qs_non_repeat))
        ls = listing_event(result_list)

        return ls

    def get(self, request, *args, **kwargs):
        res = self.get_queryset()
        res = json.dumps(res)
        return HttpResponse(res, content_type="application/json")


#Rest Api Views
class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventsSerializer
    permission_classes = [IsAuthenticated]
    permissions_required = [IsAuthenticated]

    @list_route()
    def list_all(self, request):
        events = Event.objects.all()
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)

    @list_route()
    def calendar_feed(self, request):
        try:
            start = request.query_params.get('start', '')
            end = request.query_params.get('end', '')
            start_date = datetime.datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.datetime.strptime(end, "%Y-%m-%d")
            if(start_date > end_date):
                return Response("Start date is later than end date", status=status.HTTP_400_BAD_REQUEST)
            querydict = {}
            if start_date:
                querydict['start_date__gte'] = start_date
            if end_date:
                querydict['start_date__lte'] = end_date
            querydict['is_repeat'] = False

            event_data = queryEventsForFeed(querydict, start_date, end_date)
            events = event_list(event_data)
            return Response(events)
        except ValueError:
            return Response("Date does not match format YYYY-MM-DD", status=status.HTTP_400_BAD_REQUEST)


    @list_route()
    def dashboard_feed(self, request):
        start_date = datetime.date.today()
        end_date = start_date + datetime.timedelta(days=7)
        querydict = {
            'start_date__gte': start_date,
            'start_date__lte': end_date,
            'is_repeat': False
        }

        event_data = queryEventsForFeed(querydict, start_date, end_date)
        events = dashboard_event_list(event_data)
        return Response(events)

def queryEventsForFeed(querydict, start_date, end_date):
    repeated_events = Event.objects.filter(is_repeat=True)
    non_repeated_events = Event.objects.filter(**querydict)

    temp_events = get_repeated(repeated_events, start_date, end_date)
    result_list = list(chain(temp_events, non_repeated_events))
    return result_list;