import logging
import zipfile
from io import BytesIO
from datetime import datetime
from time import strptime, mktime

from braces.views import LoginRequiredMixin
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import View
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from dataentry.models import Interceptee
from dataentry.models import InterceptionRecord
from rest_api.authentication import HasPermission
from accounts.mixins import PermissionsRequiredMixin


logger = logging.getLogger(__name__)


class PhotoExporter(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, HasPermission)
    permissions_required = ['permission_irf_view']

    def get_photos(self, start_date, end_date):
        start = timezone.make_aware(datetime.fromtimestamp(mktime(strptime(start_date, '%m-%d-%Y'))), timezone.get_default_timezone())
        end = timezone.make_aware(datetime.fromtimestamp(mktime(strptime(end_date, '%m-%d-%Y'))), timezone.get_default_timezone())

        return Interceptee.objects.filter(interception_record__date_time_of_interception__gte=start,
                                          interception_record__date_time_of_interception__lte=end).exclude(photo="").values_list('photo', 'person__full_name', 'interception_record__irf_number')

    def count_photos_in_date_range(self, request, start_date, end_date):
            return Response({"count": self.get_photos(start_date, end_date).count()})

    def export_photos(self, request, start_date, end_date):
        photos = list(self.get_photos(start_date, end_date))
        if len(photos) == 0:
            return Response({'detail' : "No photos found in specified date range"}, status = status.HTTP_400_BAD_REQUEST)

        for i in range(len(photos)):
            photos[i] = [str(x) for x in photos[i]]

        f = BytesIO()
        imagezip = zipfile.ZipFile(f, 'w')
        for photoTuple in photos:
            try:
                image_file = open(settings.MEDIA_ROOT + '/' + photoTuple[0])
                imagezip.writestr(str(photoTuple[2]) + '-' + str(photoTuple[1]) + '.jpg', image_file.read())
            except:
                logger.error('Could not find photo: ' + photoTuple[1] + '.jpg')
        imagezip.close()

        response = HttpResponse(f.getvalue(), content_type="application/zip")
        response['Content-Disposition'] = 'attachment; filename=irfPhotos ' + start_date + ' to ' + end_date + '.zip'
        return response
