from django.contrib import admin
from dataentry.models import InterceptionRecord, VictimInterview, GeoCodeLocation


class InterceptionRecordAdmin(admin.ModelAdmin):
    model = InterceptionRecord
    search_fields = ['irf_number', 'staff_name']
    list_display = ['irf_number', 'staff_name', 'number_of_victims', 'number_of_traffickers', 'date_time_of_interception', 'date_time_entered_into_system', 'date_time_last_updated']


class VictimInterviewAdmin(admin.ModelAdmin):
    model = VictimInterview
    search_fields = ['vif_number', 'interviewer']
    list_display = ['vif_number', 'interviewer', 'number_of_victims', 'number_of_traffickers', 'date', 'date_time_entered_into_system', 'date_time_last_updated']

class GeoCodeLocationAdmin(admin.ModelAdmin):
	model = GeoCodeLocation
	search_fields = ['place_name', 'latitude', 'longitude', 'level']
	list_display = ['place_name', 'latitude', 'longitude', 'level']

admin.site.register(InterceptionRecord, InterceptionRecordAdmin)
admin.site.register(VictimInterview)
admin.site.register(GeoCodeLocation)

