from rest_framework import filters as fs
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from legal.models import LegalChargeCountrySpecific
from legal.serializers import LegalChargeCountrySpecificSerializer

class LegalChargeCountrySpecificViewSet(viewsets.ModelViewSet):
    queryset = LegalChargeCountrySpecific.objects.all()
    serializer_class = LegalChargeCountrySpecificSerializer
    permission_classes = (IsAuthenticated, )
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ('charge',)
    ordering_fields = ('charge', )
    ordering = ('charge',)
    
    def get_queryset(self):
        queryset = self.queryset
        if self.action != 'list':
            return None
        in_country = self.request.GET.get('country_id')
        if in_country is not None:
            queryset = self.queryset.filter(country__id=in_country)
        
        return queryset
