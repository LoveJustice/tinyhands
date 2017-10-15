import logging

from django_filters import rest_framework as filters
from rest_framework import filters as fs
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from dataentry.helpers import related_items_helper
from dataentry.models import Address1
from dataentry.models import Address2
from dataentry.serializers import Address2Serializer, Address2RelatedItemsSerializer, Address1Serializer, Address1RelatedItemsSerializer
from rest_api.authentication import HasPermission

logger = logging.getLogger(__name__)


class Address2ViewSet(viewsets.ModelViewSet):
    queryset = Address2.objects.all().select_related('address1', 'canonical_name__address1')
    serializer_class = Address2Serializer
    permission_classes = (IsAuthenticated, HasPermission)
    permissions_required = ['permission_address2_manage']
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ('name',)
    ordering_fields = ('name', 'address1__name', 'longitude', 'latitude', 'level', 'verified', 'canonical_name__name')
    ordering = ('name',)

    @detail_route()
    def related_items(self, request, pk):
        try:
            address = Address2.objects.get(pk=pk)
        except:
            logger.error('Could not find Address2 with the following id: ' + pk)
            return Response({'detail': "Address2 not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = Address2RelatedItemsSerializer(address)
        return Response(serializer.data)

    def there_are_no_related_items(self, address):
        count = 0
        for related_items_and_ids in related_items_helper(self, address):
            count += len(related_items_and_ids['objects'])
        if count > 0:
            return False
        return True

    def destroy(self, request, pk, *args, **kwargs):
        try:
            address = Address2.objects.get(pk=pk)
        except:
            logger.error('Could not find Address2 with the following id: ' + pk)
            return Response({'detail' : "Address2 not found"}, status=status.HTTP_404_NOT_FOUND)

        if self.there_are_no_related_items(address):
            logger.info('Delete Address 2 - %s #%d', address.name, address.id)
            return super(Address2ViewSet, self).destroy(request, args, kwargs)
        else:
            logger.debug('Address2 could not be deleted due to related items on the following address1: ' + pk)
            return Response({'detail': "This Address 2 could not be deleted because it is being used by other resources"}, status=status.HTTP_409_CONFLICT)

    @detail_route()
    def swap_addresses(self, request, pk, pk2):
        try:
            address = Address2.objects.get(pk=pk)
            new_address = Address2.objects.get(pk=pk2)
        except:
            logger.error('Could not find Address2 with the following id: ' + pk)
            return Response({'detail': "Address2 not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            address2_set = address.address2_set.all()
            person_set = address.person_set.all()
            vif_set = address.victiminterview_set.all()
            viflb_set = address.victiminterviewlocationbox_set.all()

            for addr2 in address2_set:
                if addr2.id != new_address.id:
                    addr2.canonical_name = new_address
                    addr2.save()

            for person in person_set:
                person.address2 = new_address
                person.save()

            for vif in vif_set:
                vif.victim_guardian_address2 = new_address
                vif.save()

            for viflb in viflb_set:
                viflb.address2 = new_address
                viflb.save()

            affected_objects = len(address2_set) + len(person_set) + len(vif_set) + len(viflb_set)
            logger.info('Swap Address 2 - %s #%d for %s #%d - (%d) Objects Affected', address.name, address.id, new_address.name, new_address.id, affected_objects)
            logger.info('Delete Address 2 - %s #%d', address.name, address.id)
            address.delete()
        except:
            logger.error('Could not swap addresses: ' + pk + ' ' + pk2)
            return Response({'detail': "an error occurred"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"message": "success!"})


class Address1ViewSet(viewsets.ModelViewSet):
    queryset = Address1.objects.all()
    serializer_class = Address1Serializer
    permission_classes = (IsAuthenticated, HasPermission)
    permissions_required = ['permission_address2_manage']
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ('name',)
    ordering_fields = ('name', 'longitude', 'latitude', 'level', 'completed')
    ordering = ('name',)

    @list_route()
    def list_all(self, request):
        address1s = Address1.objects.all()
        serializer = self.get_serializer(address1s, many=True)
        return Response(serializer.data)

    @detail_route()
    def related_items(self, request, pk):
        try:
            address = Address1.objects.get(pk=pk)
        except:
            logger.error('Could not find Address1 with the following id: ' + pk)
            return Response({'detail': "Address1 not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = Address1RelatedItemsSerializer(address)
        return Response(serializer.data)

    @detail_route()
    def swap_addresses(self, request, pk, pk2):
        try:
            address = Address1.objects.get(pk=pk)
            new_address = Address1.objects.get(pk=pk2)
        except:
            logger.error('Could not find Address1 with the following id: ' + pk)
            return Response({'detail': "Address1 not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            address2_set = address.address2_set.all()
            person_set = address.person_set.all()
            vif_set = address.victiminterview_set.all()
            viflb_set = address.victiminterviewlocationbox_set.all()

            for addr2 in address2_set:
                addr2.address1 = new_address
                addr2.save()

            for person in person_set:
                person.address1 = new_address
                person.save()

            for vif in vif_set:
                vif.victim_guardian_address1 = new_address
                vif.save()

            for viflb in viflb_set:
                viflb.address1 = new_address
                viflb.save()

            affected_objects = len(address2_set) + len(person_set) + len(vif_set) + len(viflb_set)
            logger.info('Swap Address 1 - %s #%d for %s #%d - (%d) Objects Affected', address.name, address.id, new_address.name, new_address.id, affected_objects)
            logger.info('Delete Address 1 - %s #%d', address.name, address.id)
            address.delete()
        except:
            logger.error('Could not swap addresses: ' + pk + ' ' + pk2)
            return Response({'detail': "an error occurred"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"message": "success!"})

    def there_are_no_related_items(self, address):
        count = 0
        for related_items_and_ids in related_items_helper(self, address):
            count += len(related_items_and_ids['objects'])
        if count > 0:
            return False
        return True

    def destroy(self, request, pk, *args, **kwargs):
        try:
            address = Address1.objects.get(pk=pk)
        except:
            logger.error('Could not find Address1 with the following id: ' + pk)
            return Response({'detail': "Address1 not found"}, status=status.HTTP_404_NOT_FOUND)

        if self.there_are_no_related_items(address):
            logger.info('Delete Address 1 - %s #%d', address.name, address.id)
            return super(Address1ViewSet, self).destroy(request, args, kwargs)
        else:
            logger.debug('Address1 could not be deleted due to related items on the following address1: ' + pk)
            return Response({'detail': "This Address 1 could not be deleted because it is being used by other resources"}, status=status.HTTP_409_CONFLICT)
