from rest_framework import filters as fs
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from help.models import Video
from help.serializers import VideoSerializer

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ('title','description','tags')
    ordering_fields = ('title',)
    ordering = ('title',)