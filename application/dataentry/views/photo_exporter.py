import logging
import zipfile
from StringIO import StringIO
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


class BatchView(View, PermissionsRequiredMixin, LoginRequiredMixin):
    permissions_required = ['permission_irf_view']

    def get(self, request, startDate, endDate):
        start = timezone.make_aware(datetime.fromtimestamp(mktime(strptime(startDate, '%m-%d-%Y'))), timezone.get_default_timezone())
        end = timezone.make_aware(datetime.fromtimestamp(mktime(strptime(endDate, '%m-%d-%Y'))), timezone.get_default_timezone())

        list_of_irf_numbers = []
        irfs = InterceptionRecord.objects.all()
        for irf in irfs:
            irfDate = irf.date_time_of_interception
            if start <= irfDate <= end:
                list_of_irf_numbers.append(irf.irf_number)

        photos = list(Interceptee.objects.filter(interception_record__irf_number__in=list_of_irf_numbers).values_list('photo', 'person__full_name', 'interception_record__irf_number'))
        if len(photos) == 0:
            return render(request, 'dataentry/batch_photo_error.html')
        else:
            for i in range(len(photos)):
                photos[i] = [str(x) for x in photos[i]]

            f = StringIO()
            imagezip = zipfile.ZipFile(f, 'w')
            for photoTuple in photos:
                if photoTuple[0] == '':
                    continue
                try:
                    imageFile = open(settings.MEDIA_ROOT + '/' + photoTuple[0])
                    imagezip.writestr(photoTuple[2] + '-' + photoTuple[1] + '.jpg', imageFile.read())
                except:
                    logger.error('Could not find photo: ' + photoTuple[1] + '.jpg')
            imagezip.close()  # Close

            response = HttpResponse(f.getvalue(), content_type="application/zip")
            response['Content-Disposition'] = 'attachment; filename=irfPhotos ' + startDate + ' to ' + endDate + '.zip'
            return response


class PhotoExporter(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, HasPermission)
    permissions_required = ['permission_irf_view']

    def get_photos(self, startDate, endDate):
        start = timezone.make_aware(datetime.fromtimestamp(mktime(strptime(startDate, '%m-%d-%Y'))), timezone.get_default_timezone())
        end = timezone.make_aware(datetime.fromtimestamp(mktime(strptime(endDate, '%m-%d-%Y'))), timezone.get_default_timezone())

        return Interceptee.objects.filter(interception_record__date_time_of_interception__gte=start,
                                          interception_record__date_time_of_interception__lte=end).exclude(photo="").values_list('photo', 'person__full_name', 'interception_record__irf_number')

    def count_photos_in_date_range(self, request, startDate, endDate):
            return Response({"count": self.get_photos(startDate, endDate).count()})

    def export_photos(self, request, startDate, endDate):
        photos = list(self.get_photos(startDate, endDate))
        if len(photos) == 0:
            return Response({'detail' : "No photos found in specified date range"}, status = status.HTTP_400_BAD_REQUEST)

        for i in range(len(photos)):
            photos[i] = [str(x) for x in photos[i]]

        f = StringIO()
        imagezip = zipfile.ZipFile(f, 'w')
        for photoTuple in photos:
            try:
                image_file = open(settings.MEDIA_ROOT + '/' + photoTuple[0])
                imagezip.writestr(str(photoTuple[2]) + '-' + str(photoTuple[1]) + '.jpg', image_file.read())
            except:
                logger.error('Could not find photo: ' + photoTuple[1] + '.jpg')
        imagezip.close()

        response = HttpResponse(f.getvalue(), content_type="application/zip")
        response['Content-Disposition'] = 'attachment; filename=irfPhotos ' + startDate + ' to ' + endDate + '.zip'
        return response
