from rest_framework import status, viewsets
from rest_framework.response import Response

from dataentry.models import InterceptionAlert
from dataentry.serializers import InterceptionAlertSerializer

class InterceptionAlertViewSet(viewsets.ModelViewSet):
    queryset = InterceptionAlert.objects.all()
    serial_class = InterceptionAlertSerializer
    
    def get_interception_alerts(self, request):
        latest_id = request.GET.get('latest_id',0)
        print latest_id
        results = InterceptionAlert.objects.filter(id__gt=latest_id).order_by('id')
        print results
        #serializer = InterceptionAlertSerializer(results, many=True, context={'request': request})
        response_data = '['
        sep =''
        for result in results:
            response_data += sep + result.json
            sep=','
        response_data += ']'
        print response_data
       
        return Response(response_data)