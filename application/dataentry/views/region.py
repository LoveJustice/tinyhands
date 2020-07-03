from rest_framework import filters as fs
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from dataentry.models import Region
from dataentry.serializers import RegionSerializer
from rest_api.authentication import HasPostPermission, HasPutPermission, HasDeletePermission

class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = (IsAuthenticated, )
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ('name',)
    ordering_fields = ('name', )
    ordering = ('name',)