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

    google.maps.event.addListener(kmlLayer, 'click', function(kmlEvent) {
        var text = kmlEvent.featureData.name;
        console.log("name");
        console.log(kmlEvent.featureData.name);
        console.log("latitude");
        console.log(kmlEvent.featureData.latitude);
        console.log("longtitude")
        console.log(kmlEvent.featureData.LookAt.latitude);
        showInContentWindow(text);
        var marker = new google.maps.Marker({
              position: (kmlEvent.featureData.LookAt.latitude,kmlEvent.featureData.LookAt.longitude),
              map: map,
              title: 'my place'
        });
        google.maps.event.addListener(marker, 'click', function() {
            infowindow.open(map,marker);
        });

    });
    function showInContentWindow(text) {
      var sidediv = document.getElementById('content-window');
      sidediv.innerHTML = text;
    }


      var contentString = '<div id="content">'+
      '<div id="siteNotice">'+
      '</div>'+
      '<h1 id="firstHeading" class="firstHeading">Uluru</h1>'+
      '<div id="bodyContent">'+
      '<p><b>Uluru</b>, also referred to as <b>Ayers Rock</b>, is a large ' +
      'sandstone rock formation in the southern part of the '+
      'Northern Territory, central Australia. It lies 335&#160;km (208&#160;mi) '+
      'south west of the nearest large town, Alice Springs; 450&#160;km '+
      '(280&#160;mi) by road. Kata Tjuta and Uluru are the two major '+
      'features of the Uluru - Kata Tjuta National Park. Uluru is '+
      'sacred to the Pitjantjatjara and Yankunytjatjara, the '+
      'Aboriginal people of the area. It has many springs, waterholes, '+
      'rock caves and ancient paintings. Uluru is listed as a World '+
      'Heritage Site.</p>'+
      '<p>Attribution: Uluru, <a href="http://en.wikipedia.org/w/index.php?title=Uluru&oldid=297882194">'+
      'http://en.wikipedia.org/w/index.php?title=Uluru</a> '+
      '(last visited June 22, 2009).</p>'+
      '</div>'+
      '</div>';

  var infowindow = new google.maps.InfoWindow({
      content: contentString
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