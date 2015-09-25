from django.contrib import admin

# Register your models here.
# admin.autodiscover()
from events.models import Event

admin.site.register(Event)