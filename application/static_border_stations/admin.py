from django.contrib import admin
from static_border_stations.models import Staff, CommitteeMember, Location


class PersonAdminModel(admin.ModelAdmin):
    search_fields = ['email', 'first_name', 'last_name']
    list_display = ['email', 'first_name', 'last_name']


class StaffAdmin(PersonAdminModel):
    model = Staff


class LocationAdmin(admin.ModelAdmin):
    search_fields = ['border_station', 'name', 'latitude', 'longitude', ]
    list_display = ['border_station', 'name', 'latitude', 'longitude', ]
    model = Location


class CommitteeMemberAdmin(PersonAdminModel):
    model = CommitteeMember


admin.site.register(Staff, StaffAdmin)
admin.site.register(CommitteeMember, CommitteeMemberAdmin)
admin.site.register(Location, LocationAdmin)




