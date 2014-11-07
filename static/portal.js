function initialize() {
    var mapOptions = {
      center: { lat: 28.394857, lng: 84.124008},
      zoom: 8,
      streetViewControl: false
    };
    var map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
    getBorderStations(map);
    createVDCOverlay(map);
}


function createVDCOverlay(map){
    var VDCLayer = new google.maps.FusionTablesLayer({
            query: {
              select: 'col13',
              from: '1r-omWhMz1wzQG3-e55K7dmCetVe3fRWX4Ai4G_U1'
            },
            styles: [{
          polygonOptions: {
            fillOpacity: 0.2
          }}],
          options: {
            styleId: 2,
            templateId: 2
          }});
        VDCLayer.setMap(map);
}

//var map;

function resizeMap() {
    var map_canvas = document.getElementById('map-canvas');
    map_canvas.style.width = window.innerWidth+"px";
    map_canvas.style.height = (window.innerHeight-50)+"px";
}

function getContentString(borderStation){
	return '<div class="dashboardInfoWindow">' +
	    '<h3>'+borderStation.fields.station_name+'</h3>' +
	    '<p>'+borderStation.fields.station_code+'</p>' +
	    '</div>';

}

function getBorderStations(map){
    $.get("/portal/get_border_stations",function(data,status){
        var infowindow = new google.maps.InfoWindow({});
        for(var station=0;station<data.length;station++){
            //
            var myLatlng = new google.maps.LatLng(data[station].fields.latitude,data[station].fields.longitude);
            var marker = new google.maps.Marker({
                position: myLatlng,
                map: map,
                title: data[station].fields.station_name + " " + data[station].fields.station_code
            });
            google.maps.event.addListener(marker, 'mouseout', (function(marker, station) {
                return function() {
                    infowindow.close();
                }
            })(marker, station));
            google.maps.event.addListener(marker, 'mouseover', (function(marker, station) {
                return function() {
                    infowindow.setContent(getContentString(data[station]));
                    infowindow.open(map, this);
                }
            })(marker, station));
        }
    });
}

$( window ).resize(function() {
  resizeMap();
});

$(function() {
    google.maps.event.addDomListener(window, 'load', initialize);
    resizeMap();
});

