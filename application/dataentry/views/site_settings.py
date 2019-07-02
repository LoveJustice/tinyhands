import os
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from dataentry.models import SiteSettings
from dataentry.serializers import  SiteSettingsSerializer
from rest_api.authentication import IsSuperAdministrator
from rest_framework.response import Response


class SiteSettingsViewSet(viewsets.ModelViewSet):
    queryset = SiteSettings.objects.all()
    serializer_class = SiteSettingsSerializer
    permission_classes = (IsAuthenticated, IsSuperAdministrator)

    def retrieve_custom(self, request, *args, **kwargs):
        site_settings = SiteSettings.objects.all()[0]
        return Response(SiteSettingsSerializer(site_settings).data)
    
    def retrieve_google_map_key(self, request):
        key_file = os.environ['GOOGLE_MAP_KEY']
        try:
            with open (key_file, "r") as myfile:
                google_map_key=myfile.read()
        except:
            # when we can't read the key, send back an empty string
            # This will cause the map to display in development mode
            google_map_key = ''
            
        return Response(google_map_key.rstrip())
