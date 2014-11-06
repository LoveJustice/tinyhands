function initialize() {
    var mapOptions = {
      center: { lat: 28.394857, lng: 84.124008},
      zoom: 8,
      streetViewControl: false
    };
    var map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

    var homeControlDiv = document.createElement('div');
    var homeControl = new HomeControl(homeControlDiv, map);

    homeControlDiv.index = 1;
    map.controls[google.maps.ControlPosition.TOP_RIGHT].push(homeControlDiv);

    function getContentString(borderStation){
	return '<div>' +
	    '<h3>'+borderStation.fields.station_name+'</h3>' +
	    '<p>'+borderStation.fields.station_code+'</p>' +
	    '</div>';	    
    }

    $.get("/portal/get_border_stations",function(data,status){
        console.log(data);
        var border_stations = data;
        var infowindow = new google.maps.InfoWindow({
            maxWidth: 400
        });
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
                    infowindow.close();
		            infowindow.setContent(getContentString(data[station]));
                    infowindow.open(map, marker);
                }
            })(marker, station));
        }
    });

}

//var map;
var chicago = new google.maps.LatLng(41.850033, -87.6500523);

function HomeControl(controlDiv, map) {

  // Set CSS styles for the DIV containing the control
  // Setting padding to 5 px will offset the control
  // from the edge of the map
  controlDiv.style.padding = '5px';

  // Set CSS for the control border
  var controlUI = document.createElement('div');
  controlUI.style.backgroundColor = 'white';
  controlUI.style.borderStyle = 'solid';
  controlUI.style.borderWidth = '2px';
  controlUI.style.cursor = 'pointer';
  controlUI.style.textAlign = 'center';
  controlUI.title = 'Click to set the map to Home';
  controlDiv.appendChild(controlUI);

  // Set CSS for the control interior
  var controlText = document.createElement('div');
  controlText.style.fontFamily = 'Arial,sans-serif';
  controlText.style.fontSize = '12px';
  controlText.style.paddingLeft = '4px';
  controlText.style.paddingRight = '4px';
  controlText.innerHTML = '<b>Add New Station</b>';
  controlUI.appendChild(controlText);

  // Setup the click event listeners: simply set the map to
  // Chicago
  //google.maps.event.addDomListener(controlUI, 'click', function() {
     // map.setCenter(chicago)
  google.maps.event.addListener(map, 'click', function(event){
      alert('Lat: ' + event.latLng.lat() + ' Lng: ' + event.latLng.lng());

  //});
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

