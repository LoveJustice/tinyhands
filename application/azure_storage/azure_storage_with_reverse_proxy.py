from django.urls import reverse
from storages.backends.azure_storage import AzureStorage

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

        path = self._get_valid_path(name)

        # This requires you to have a AzureStorageProxyView to serve the file with the right url
        return reverse('proxy_to_serve_azure_file', kwargs={'path': path})
