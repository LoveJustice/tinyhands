# from django.urls import reverse
# from storages.backends.azure_storage import AzureStorage
#
#
# class AzureStorageWithReverseProxy(AzureStorage):
#     """
#     This class is used to return urls that are on our domain instead of the Azure domain.
#     This helps us keep Django security by tunneling through our backend to Azure
#     """
#
#     def url(self, name, *args, **kwargs):
#         print('Hello')
#         # This requires you to have a AzureStorageProxyView to serve the file with the right url
#         return reverse('proxy_to_serve_azure_file', kwargs={'path': name})
#
#     def generate_filename(self, filename):
#         # This requires you to have a AzureStorageProxyView to serve the file with the right url
#         return reverse('proxy_to_serve_azure_file', kwargs={'path': filename})
