from dataentry.models import BorderStation

def border_stations_processor(request):
	border_stations = BorderStation.objects.order_by('station_name')
 	return {'border_stations': border_stations}
