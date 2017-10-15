import logging

from django_filters import rest_framework as filters

from rest_framework import filters as fs
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from dataentry.models import Country
from dataentry.serializers import CountrySerializer
from rest_api.authentication import HasPostPermission, HasPutPermission, HasDeletePermission

logger = logging.getLogger(__name__)

class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = (IsAuthenticated, HasPostPermission, HasPutPermission, HasDeletePermission)
    post_permissions_required = ['permission_address2_manage']
    put_permissions_required = ['permission_address2_manage']
    delete_permissions_required = ['permission_address2_manage']
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ('name',)
    ordering_fields = ('name', 'longitude', 'latitude', 'zoom_level')
    ordering = ('name',)
