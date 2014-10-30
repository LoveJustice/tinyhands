/**
 * Created by rszempli on 10/28/14.
 */
function initialize() {
    var mapOptions = {
      center: { lat: 28.394857, lng: 84.124008},
      zoom: 8,
      streetViewControl: false
    };

    var map = new google.maps.Map(document.getElementById('map-canvas'),
        mapOptions);

    var kmlLayer = new google.maps.KmlLayer({
        url: 'https://docs.google.com/uc?authuser=0&id=0Bz3L11M8_D-MbWkwT2R5ZDVOUms&export=download',
        suppressInfoWindows: true,
        map: map
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