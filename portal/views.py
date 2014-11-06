from django.http import HttpResponse
from django.shortcuts import render
from django.core import serializers

from dataentry.models import BorderStation

def main_dashboard(request):
    return render(request, "portal/main_dashboard.html")

def get_border_stations(request):
    border_stations = serializers.serialize("json", BorderStation.objects.all())
    return HttpResponse(border_stations, content_type="application/json")

def create_border_stations(request):
    if 'station_code' in request.GET and 'station_name' in request.GET and 'latitude' in request.GET and 'longitude' in request.GET:
        name = request.GET['station_name']
        code = request.GET['station_code']
        lat = request.GET['latitude']
        long = request.GET['longitude']
        BorderStation.objects.create(station_code=code, station_name=name, latitude=lat, longitude=long)
        return HttpResponse([name,code,lat,long])
    else:
        return HttpResponse("Error")

