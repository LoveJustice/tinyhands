import datetime
import json
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q, F
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import CreateView, ListView, TemplateView, DeleteView, UpdateView
from events.forms import EventForm
from events.helpers import format_schedule, get_repeated, event_list, dashboard_event_list
from events.models import Event
from itertools import chain


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
            querydict = {}
            querydict['start_date__gte'] = start_date
            querydict['start_date__lte'] = end_date
            querydict['is_repeat'] = False
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
        print result_list
        ls = listing_event(result_list)

        print ls
        return ls

    def get(self, request, *args, **kwargs):
        res = self.get_queryset()
        res = json.dumps(res)
        return HttpResponse(res, content_type="application/json")


