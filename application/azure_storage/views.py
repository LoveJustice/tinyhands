from azure.core.exceptions import ResourceNotFoundError
from django.core.files.storage import default_storage
from django.http import FileResponse, Http404
from django.views import View
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
import re

# WARN: These rules must match Azure's blob naming rules
def remove_hidden_whitespace_characters(string: str):
    """
    Removes the following Unicode characters:
      - Non-breaking space (\u00A0)
      - Zero-width space (\u200B)
      - Zero-width non-joiner (\u200C)
      - Zero-width joiner (\u200D)
      - Zero-width no-break space (\uFEFF)
      - Narrow no-break space (\u202F)
    """
    pattern = r'[\u00A0\u200B\u200C\u200D\uFEFF\u202F]'
    return re.sub(pattern, '', string)

class AzureStorageReverseProxyView(APIView):
    # Gives 401 Unauthorized locally without nginx
    # Nginx converts browser cookie into authentication
    permission_classes = (IsAuthenticated, )
    def get(self, request, *args, **kwargs):
        # Roughly copied from DjangoStreamingServer.serve(private_file)
        # in django-private-storages open source project
        # Assumes your default_storage is AzureStorageWithReverseProxy
        try:
            path = self.kwargs['path']
            cleaned_path = remove_hidden_whitespace_characters(path)

            file = default_storage.open(cleaned_path)
            response = FileResponse(file)
        except ResourceNotFoundError:
            raise Http404
        return response
