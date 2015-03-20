function initialize() {
    var mapOptions = {
      center: { lat: 28.394857, lng: 84.124008},
      zoom: 8,
      streetViewControl: false
    };

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



    var map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
    var homeControlDiv = document.createElement('div');
    var homeControl = new HomeControl(VDCLayer, homeControlDiv, map);
    homeControlDiv.index = 1;
    map.controls[google.maps.ControlPosition.TOP_RIGHT].push(homeControlDiv);

    getBorderStations(map);
    createVDCOverlay(VDCLayer, map);
}

var hidden = false;

function HomeControl(layer, controlDiv, map) {
  controlDiv.style.padding = '6px';
  // Set CSS for the control border
  var controlUI = document.createElement('div');
  controlUI.style.backgroundColor = 'white';
  controlUI.style.borderStyle = 'solid';
  controlUI.style.borderWidth = '.5px';
  controlUI.style.cursor = 'pointer';
  controlUI.style.textAlign = 'center';
  controlUI.title = 'Click to toggle VDC Overlay';
  controlDiv.appendChild(controlUI);

  // Set CSS for the control interior
  var controlText = document.createElement('div');
  controlText.style.fontFamily = 'Arial,sans-serif';
  controlText.style.fontSize = '12px';
  controlText.style.paddingLeft = '4px';
  controlText.style.paddingRight = '4px';
  controlText.innerHTML = '<b>VDC Layer On/Off</b>';
  controlUI.appendChild(controlText);

  google.maps.event.addDomListener(controlUI, 'click', function() {
      toggleVDCOverlay(layer, map);
  });

}

function createVDCOverlay(layer, map) {
    layer.setMap(map);
}

function toggleVDCOverlay(layer, map) {
    if(!hidden) {
        layer.setMap(null);
        hidden = true;
    }
    else {
        layer.setMap(map);
        hidden = false;
    }
}

function resizeMap() {
    var map_canvas = document.getElementById('map-canvas');
    map_canvas.style.width = window.innerWidth+"px";
    map_canvas.style.height = (window.innerHeight-50)+"px";
}

function getContentString(borderStation){
    return '<div id="StationWindow" class="dashboardInfoWindow">' +
	    '<h3>'+borderStation.fields.station_name+'</h3>' +
	    '<p>'+borderStation.fields.station_code+'</p>' +
        '<p>Shelter: '+borderStation.fields.has_shelter+'</p>' +
        '<p id="stationInterception">Interceptions: ' + '</p>' +
	    '</div>';
}

function getBorderStations(map){
    $.get("/portal/get_border_stations",function(data,status){
        var infowindow = new google.maps.InfoWindow({maxWidth: 1000});
        var dynamicWindow = new google.maps.InfoWindow({maxWidth: 1000});
        for(var station=0;station<data.length;station++){
            var myLatlng = new google.maps.LatLng(data[station].fields.latitude,data[station].fields.longitude);
            var marker = new google.maps.Marker({
                position: myLatlng,
                map: map,
                title: data[station].fields.station_name + " " + data[station].fields.station_code
            });
            google.maps.event.addListener(marker, 'mouseout', (function(marker, station) {
                return function() {
                    infowindow.close();
                    $(".gm-style-iw").each(function() {
                        $(this).removeClass('station-info-window');
                    });
                }
            })(marker, station));
            google.maps.event.addListener(marker, 'mouseover', (function(marker, station) {
                return function() {
                    infowindow.setContent(getContentString(data[station]));
                    console.log(data[station].fields.station_name);
                    $.get("/portal/get_interception_records", {station_code: data[station].fields.station_code}, function(data){
                        $("#stationInterception").text("Interceptions: " + data);
                    });

                    infowindow.open(map, this);
                    $(".gm-style-iw").each(function() {
                        if(data[station].fields.station_name.length > 10) {
                            $(this).addClass('station-info-window-big');
                            console.log(data[station].station_code);
                        }
                        $(this).addClass('station-info-window');
                    });
                }
            })(marker, station));

            google.maps.event.addListener(marker, 'click', (function(marker, station) {
                return function() {
                    infowindow.close();
                    dynamicWindow.setContent(getContentString(data[station]));
                    console.log(data[station].fields.station_name);
                    $.get("/portal/get_interception_records", {station_code: data[station].fields.station_code}, function(data){
                        $("#stationInterception").text("Interceptions: " + data);
                    });

                    dynamicWindow.open(map, this);
                    $(".gm-style-iw").each(function() {
                        if(data[station].fields.station_name.length > 10) {
                            $(this).addClass('station-info-window-big');
                            console.log(data[station].station_code);
                        }
                        $(this).addClass('station-info-window');
                    });
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

