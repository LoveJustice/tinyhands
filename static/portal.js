function initialize() {
    var mapOptions = {
      center: { lat: 28.394857, lng: 84.124008},
      zoom: 8,
      streetViewControl: false
    };

    var map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

    function getContentString(borderStation){
        return borderStation.fields.station_name + ' '  + borderStation.fields.station_code;
    }

    $.get("/portal/get_border_stations",function(data,status){
        console.log(data);
        var border_stations = data;
        for(station=0;station<data.length;station++){
            var myLatlng = new google.maps.LatLng(data[station].fields.latitude,data[station].fields.longitude);
            console.log(myLatlng)
            var marker = new google.maps.Marker({
              position: myLatlng,
              map: map,
              title: data[station].fields.station_name + " " + data[station].fields.station_code
            });
            google.maps.event.addListener(marker, 'click', (function(marker, station) {
                return function() {
                    var infowindow = new google.maps.InfoWindow({ });
                    infowindow.setContent(getContentString(data[station]));
                    infowindow.open(map, marker);
                }
            })(marker, station));
        }
    });

}

function resizeMap() {
    var map_canvas = document.getElementById('map-canvas');
    map_canvas.style.width = window.innerWidth+"px";
    map_canvas.style.height = (window.innerHeight-50)+"px";
}

$( window ).resize(function() {
  resizeMap();
});

$(function() {
    google.maps.event.addDomListener(window, 'load', initialize);
    resizeMap();
});

