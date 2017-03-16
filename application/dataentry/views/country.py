import logging

from rest_framework import filters
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from dataentry.helpers import related_items_helper
from dataentry.models import Country
from dataentry.serializers import CountrySerializer
from rest_api.authentication import HasPermission

logger = logging.getLogger(__name__)

class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = (IsAuthenticated,)
    permissions_required = []
    filter_backends = (filters.SearchFilter, filters.OrderingFilter,)
    search_fields = ('name',)
    ordering_fields = ('name', 'longitude', 'latitude', 'zoom_level')
    ordering = ('name',)
