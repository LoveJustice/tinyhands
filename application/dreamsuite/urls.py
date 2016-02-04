from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'dataentry.views.home', name='home'),
    url(r'^data-entry/', include('dataentry.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^events/', include('events.urls')),
    url(r'^static_border_stations/', include('static_border_stations.urls')),
    url(r'^portal/', include('portal.urls')),
    url(r'^budget/', include('budget.urls')),
    url(r'^api/', include('rest_api.urls')),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    url(r'^password_reset/$', 'django.contrib.auth.views.password_reset', name='password_reset'),
    url(r'^password_reset/done/$', 'django.contrib.auth.views.password_reset_done', name='password_reset_done'),
    # Support old style base36 password reset links; remove in Django 1.7
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm',
        name='password_reset_confirm'),
    url(r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete', name='password_reset_complete'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^interceptee_fuzzy_matching/', 'dataentry.views.interceptee_fuzzy_matching', name='interceptee_fuzzy_matching'),
    url(r'^get_station_id/', 'dataentry.views.get_station_id', name='get_station_id'),

) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
