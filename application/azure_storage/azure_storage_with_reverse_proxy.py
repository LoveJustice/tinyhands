from django.urls import reverse
from storages.backends.azure_storage import AzureStorage
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

class AzureStorageWithReverseProxy(AzureStorage):
    """
    This class is used to return urls that are on our domain instead of the Azure domain.
    This helps us keep Django security by tunneling through our backend to Azure
    """

    def url(self, name, *args, **kwargs):
        # Without this, this would call AzureStorage.url() which returns a Azure domain url
        # (xxx.blob.core.windows.net/rest/of/path)
        #     container_blob_url = self.custom_client.get_blob_client(name).url
        #     return BlobClient.from_blob_url(container_blob_url, credential=credential).url

        name = remove_hidden_whitespace_characters(name)

        path = self._get_valid_path(name)

        # This requires you to have a AzureStorageProxyView to serve the file with the right url
        return reverse('proxy_to_serve_azure_file', kwargs={'path': path})
