from django.urls import re_path
from .views import FaceMatchingViewSet
from . import views

urlpatterns = [
    # path('', views.home, name='home'),
    # path('compare/', views.compare_photos, name='compare_photos'),
    # path('select/', views.select_from_records, name='select_from_records'),
    # path('upload/', views.upload_photo, name='upload_photo'),
    # path('take/', views.take_photo, name='take_photo'),

    #  Get matches for encoded 
    re_path(r'^face-matching/upload/$', FaceMatchingViewSet.as_view({'post': 'get_upload_matches'}), name='FaceMatchesList'),
]