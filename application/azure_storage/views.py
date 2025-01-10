from azure.core.exceptions import ResourceNotFoundError
from django.core.files.storage import default_storage
from django.http import FileResponse, Http404
from django.views import View
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


class AzureStorageReverseProxyView(APIView):
    # Gives 401 Unauthorized locally without nginx
    # Nginx converts browser cookie into authentication
    permission_classes = (IsAuthenticated, )
    def get(self, request, *args, **kwargs):
        # Roughly copied from DjangoStreamingServer.serve(private_file)
        # in django-private-storages open source project
        # Assumes your default_storage is AzureStorageWithReverseProxy
        try:
            file = default_storage.open(self.kwargs['path'])
            response = FileResponse(file)
        except ResourceNotFoundError:
            raise Http404
        return response
