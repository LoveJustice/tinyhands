from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'dataentry.views.home', name='home'),
    url(r'^data-entry/', include('dataentry.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),

    url(r'^admin/', include(admin.site.urls)),
)
