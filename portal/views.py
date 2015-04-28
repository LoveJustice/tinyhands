from django.http import HttpResponse
from django.shortcuts import render
from django.core import serializers
from django.contrib.auth.decorators import login_required
from dataentry.models import BorderStation
from dataentry.models import InterceptionRecord
from django.core.urlresolvers import reverse
import ipdb


@login_required
def main_dashboard(request):
    return render(request, "portal/main_dashboard.html")


@login_required
def get_border_stations(request):
    border_stations = serializers.serialize("json", BorderStation.objects.all())
    return HttpResponse(border_stations, content_type="application/json")


def get_interception_records(request):
    if "station_code" in request.REQUEST:
        interception_records = InterceptionRecord.objects.filter(irf_number__startswith=request.REQUEST["station_code"])
        return HttpResponse(interception_records.count())
    return HttpResponse("No IRFs Found")

def get_staff_count(request):
    if "station_code" in request.REQUEST:
        border_station = BorderStation.objects.filter(station_code=request.REQUEST["station_code"]).first()
        return HttpResponse(border_station.staff_set.count())
    return HttpResponse("No station found")

