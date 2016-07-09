from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta
from django.utils import timezone
from dataentry.models import BorderStation, InterceptionRecord


@login_required
def main_dashboard(request):
    return render(request, "portal/main_dashboard.html", {'settings': settings})


@login_required
def get_border_stations(request):
    border_stations = serializers.serialize("json", BorderStation.objects.all())
    return HttpResponse(border_stations, content_type="application/json")


def get_interception_records(request):
    interceptionSum = 0
    if "station_code" in request.GET:
        interception_records = InterceptionRecord.objects.filter(irf_number__startswith=request.GET["station_code"])
        for interception in interception_records:
            victims = interception.interceptees.filter(kind='v')
            interceptionSum += len(victims)
        return HttpResponse(interceptionSum)
    return HttpResponse("No IRFs Found")


def get_staff_count(request):
    if "station_code" in request.GET:
        border_station = BorderStation.objects.filter(station_code=request.GET["station_code"]).first()
        return HttpResponse(border_station.staff_set.count())
    return HttpResponse("No station found")


class TallyDaysView(APIView):

    def get(self, request):
        # timezone.now() gets utc time but timezone.now().now() gets local Nepal time
        today = timezone.now().now()
        dates = [today - timedelta(days=x) for x in range(7)]
        results = {}
        results['id'] = request.user.id
        foo = []
        i = 0
        for date in dates:
            day_records = {}
            day_records['date'] = date
            day_records['interceptions'] = {}
            interceptions = day_records['interceptions']
            records = InterceptionRecord.objects.filter(date_time_of_interception__year=date.year, date_time_of_interception__month=date.month, date_time_of_interception__day=date.day)
            for record in records:
                station_code = record.irf_number[:3]
                victims = record.interceptees.filter(kind='v')
                count = len(victims)
                if station_code not in interceptions.keys():
                    interceptions[station_code] = 0
                interceptions[station_code] += count
            foo.append(day_records)
            i += 1
        results['days'] = foo
        return Response(results, status=status.HTTP_200_OK)
