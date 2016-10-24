import csv
from datetime import date

from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from dataentry.models import InterceptionRecord, VictimInterview
from export_import import irf_io, vif_io
from rest_api.authentication import HasPermission


class IrfCsvExportView(APIView):
    permission_classes = [IsAuthenticated, HasPermission]
    permissions_required = ['permission_irf_view']

    def get(self, request, format=None):
        response = HttpResponse(content_type='text/csv')
        today = date.today()
        response['Content-Disposition'] = 'attachment; filename=irf-all-data-%d-%d-%d.csv' % (
            today.year, today.month, today.day)

        writer = csv.writer(response)
        irfs = InterceptionRecord.objects.all()
        csv_rows = irf_io.get_irf_export_rows(irfs)
        writer.writerows(csv_rows)

        return response


class VifCsvExportView(APIView):
    permission_classes = [IsAuthenticated, HasPermission]
    permissions_required = ['permission_vif_view']

    def get(self, request, format=None):
        response = HttpResponse(content_type='text/csv')
        today = date.today()
        response['Content-Disposition'] = 'attachment; filename=vif-all-data-%d-%d-%d.csv' % (
            today.year, today.month, today.day)

        writer = csv.writer(response)
        vifs = VictimInterview.objects.all()
        csv_rows = vif_io.get_vif_export_rows(vifs)
        writer.writerows(csv_rows)

        return response