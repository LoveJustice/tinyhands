import json

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from dataentry.models import InterceptionAlert
from dataentry.serializers import InterceptionAlertSerializer

class InterceptionAlertViewSet(viewsets.ModelViewSet):
    serializer_class = InterceptionAlertSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        latest_id = self.request.GET.get('latest_id',0)
        return InterceptionAlert.objects.filter(id__gt=latest_id).order_by('id')