from django.http import HttpResponse
from django.shortcuts import render
from django.core import serializers

from dataentry.models import BorderStation

def main_dashboard(request):
    return render(request, "portal/main_dashboard.html")

def get_border_stations(request):
    border_stations = serializers.serialize("json", BorderStation.objects.all())
    return HttpResponse(border_stations, content_type="application/json")
