from django.urls import path, re_path

from azure_storage.views import AzureStorageReverseProxyView

urlpatterns = [
  re_path('^(?P<path>.*)$', AzureStorageReverseProxyView.as_view(), name='proxy_to_serve_azure_file'),
]
