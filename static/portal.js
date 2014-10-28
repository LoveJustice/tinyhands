/**
 * Created by rszempli on 10/28/14.
 */
function initialize() {
    var mapOptions = {
      center: { lat: 28.394857, lng: 84.124008},
      zoom: 8
    };

    var map = new google.maps.Map(document.getElementById('map-canvas'),
        mapOptions);
}

function resizeMap() {
    var mapcanv = document.getElementById('map-canvas');
    mapcanv.style.width = window.innerWidth+"px";
    mapcanv.style.height = (window.innerHeight-50)+"px";
}

$( window ).resize(function() {
  resizeMap();
});

$(function() {
    google.maps.event.addDomListener(window, 'load', initialize);
    resizeMap();
});