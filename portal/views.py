from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta
from django.utils import timezone
from dataentry.models import BorderStation, InterceptionRecord

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


class TallyDaysView(APIView):

    def get(self, request):
        days = ['Monday', 'Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        #timezone.now() gets utc time but timezone.now().now() gets local Nepal time
        today = timezone.now().now()
        dates = [today - timedelta(days=x) for x in range(7)]
        results = {}
        i = 0
        for date in dates:
            day_records = {}
            if(i==0):
                day_records['dayOfWeek'] = "Today"
            else:
                day_records['dayOfWeek'] = days[date.weekday()]
            day_records['interceptions'] = {}
            interceptions = day_records['interceptions']
            records = InterceptionRecord.objects.filter(date_time_of_interception__year=date.year, date_time_of_interception__month=date.month, date_time_of_interception__day=date.day)
            for record in records:
                station_code = record.irf_number[:3]
                victims = record.interceptees.filter(kind='v')
                count = len(victims)
                if station_code not in interceptions.keys():
                   interceptions[station_code] = 0
                interceptions[station_code]+=count
            results[i] = day_records
            i+=1

        return Response(results, status=status.HTTP_200_OK);

