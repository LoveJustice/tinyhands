import json

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_api.authentication import HasPermission

from dataentry.models import InterceptionAlert
from dataentry.serializers import InterceptionAlertSerializer

class InterceptionAlertViewSet(viewsets.ModelViewSet):
    queryset = InterceptionAlert.objects.all()
    serial_class = InterceptionAlertSerializer
    permission_classes = (IsAuthenticated, HasPermission)
    permissions_required = []
    
    def get_interception_alerts(self, request):
        latest_id = request.GET.get('latest_id',0)
        results = self.queryset.filter(id__gt=latest_id).order_by('id')
        return Response([json.loads(alert.json) for alert in results])