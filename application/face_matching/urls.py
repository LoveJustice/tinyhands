from django.conf.urls import url
from .views import FaceMatchingViewSet
from . import views

urlpatterns = [
    # path('', views.home, name='home'),
    # path('compare/', views.compare_photos, name='compare_photos'),
    # path('select/', views.select_from_records, name='select_from_records'),
    # path('upload/', views.upload_photo, name='upload_photo'),
    # path('take/', views.take_photo, name='take_photo'),

    #  Get list of person_ids with face_encodings
    #  Get matches for encoded 
    url(r'^face-matching/upload/$', FaceMatchingViewSet.as_view({'post': 'get_upload_matches'}), name='FaceMatchesList'),
]