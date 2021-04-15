from rest_framework import filters as fs
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from dataentry.models import ClientDiagnostic
from dataentry.serializers import ClientDiagnosticSerializer

class ClientDiagnosticViewSet(viewsets.ModelViewSet):
    queryset = ClientDiagnostic.objects.all()
    serializer_class = ClientDiagnosticSerializer
    permission_classes = (IsAuthenticated, )
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ('user_name',)
    ordering_fields = ('user_name',)
    ordering = ('user_name',)