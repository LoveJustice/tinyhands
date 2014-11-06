from dataentry.models import BorderStation

def border_stations_processor(request):
	border_stations = BorderStation.objects.all()            
 	return {'border_stations': border_stations}