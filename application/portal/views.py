from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from dataentry.models import Interceptee
from dataentry.models import InterceptionRecord


class TallyDaysView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        # timezone.now() gets utc time but timezone.now().now() gets local Nepal time
        today = timezone.now().now()
        dates = [today - timedelta(days=x) for x in range(7)]
        results = {'id': request.user.id}
        foo = []
        i = 0
        for date in dates:
            day_records = {'date': date, 'interceptions': {}}
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
        results['ytd'] = Interceptee.objects.filter(kind='v', interception_record__date_time_of_interception__year=today.year).count()

        return Response(results, status=status.HTTP_200_OK)
