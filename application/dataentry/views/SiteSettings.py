from rest_framework import viewsets

from dataentry.models import FuzzyMatching
from dataentry.serializers import SysAdminSettingsSerializer


class SysAdminSettingsViewSet(viewsets.ModelViewSet):
    queryset = FuzzyMatching.objects.all()
    serializer_class = SysAdminSettingsSerializer
