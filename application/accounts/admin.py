from django.contrib import admin
from accounts.models import *

admin.site.register(DefaultPermissionsSet)
admin.site.register(Account)
admin.site.register(Alert)
