from django.http import HttpResponse
from django.shortcuts import render
from django.core import serializers
from django.contrib.auth.decorators import login_required

from dataentry.models import BorderStation

@login_required
def main_dashboard(request):
    return render(request, "portal/main_dashboard.html")

@login_required
def get_border_stations(request):
    border_stations = serializers.serialize("json", BorderStation.objects.all())
    return HttpResponse(border_stations, content_type="application/json")
