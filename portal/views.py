from django.http import HttpResponse
from django.shortcuts import render
from django.core import serializers
from django.contrib.auth.decorators import login_required
from dataentry.models import BorderStation
from dataentry.models import InterceptionRecord

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
    return HttpResponse("No IRFs Not Found")