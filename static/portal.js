function initialize() {
    //initialize the map
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

function resizeMap() { // keeping the controls visibile on the page at all times
    var map_canvas = document.getElementById('map-canvas');
    map_canvas.style.width = window.innerWidth+"px";
    map_canvas.style.height = (window.innerHeight-50)+"px";
}

function getStaticContentString(borderStation) { //This is what the content of a static border_station is
    return '<div id="Static'+borderStation.fields.station_code+'" class="dashboardInfoWindow">' +
        '<h3>' + borderStation.fields.station_name + ' - ' + borderStation.fields.station_code + '</h3>' +

        '<p>Est. ' + borderStation.fields.date_established + '</p>' +
        '<p>Has shelter: ' + hasShelter(borderStation) + '</p>' +
        '<p id="stationInterception">Interceptions: ' + '</p>' +
        '<p id="staffset"># of Staff ' + '</p>' +
        '</div>';
}


function getDynamicContentString(borderStation){ //This is what the content of a static border_station is
    return '<div id="Dynamic'+borderStation.fields.station_code+'" class="dynamicInfoWindow">' +
        '<h3>' + borderStation.fields.station_name + ' - ' + borderStation.fields.station_code + '</h3>' +
        '<div id="leftColumn" class="col-md-6">'+


            '<p>Est. ' + borderStation.fields.date_established + '</p>' +
            '<p>Has shelter: ' + hasShelter(borderStation) + '</p>' +
            '<p id="stationInterception">Interceptions: ' + '</p>' +
            '<p id="staffset"># of Staff ' + '</p>' +
        '</div>'+

        '<div id="rightColumn" class="col-md-6">'+
            '<p id="BS"><a href="/static_border_stations/border-stations/' + borderStation.pk + '">Subcommittee, Staff, and Locations</a>' + '</p>' +
            '<p id="irf"><a href="/data-entry/irfs/search/?search_value=' + borderStation.fields.station_code + '">IRFs</a>' + '</p>' +
            '<p id="vif"><a href="/data-entry/vifs/search/?search_value=' + borderStation.fields.station_code + '">VIFs</a>' + '</p>' +
        '</div>'+
    '</div>';
}



function getBorderStations(map){
    /*  Runs on page load to show all the border stations on the
     *  map and set all of the onClick/onHover events for them
     */
    $.get("/portal/get_border_stations",function(data, status){
        var infowindow = new google.maps.InfoWindow(); //Initialize the Static Border Station view

        var dynamicWindow = new google.maps.InfoWindow(); //Initialize the Dynamic Border Station view


        for(var station=0;station<data.length;station++){ //Iterate over each Border Station
            var myLatlng = new google.maps.LatLng(data[station].fields.latitude,data[station].fields.longitude);
            var marker = new google.maps.Marker({ //Initialize a BorderStation's marker
                position: myLatlng,
                map: map,
                title: data[station].fields.station_name + " " + data[station].fields.station_code,
                clicked: false,
                optimized: false
            });

            google.maps.event.addListener(dynamicWindow, 'closeclick', (function(marker) {
                return function() {
                    toggleMarkerClick(marker);
                }
            })(marker));


            google.maps.event.addListener(marker, 'mouseout', (function(marker, station) {
                return function() {
                    infowindow.close();
                    $(".gm-style-iw").each(function() {
                        $(this).removeClass('station-info-window');
                    });
                }
            })(marker, station));

            google.maps.event.addListener(marker, 'mouseover', (function(marker, station) { //For the Static View
                return function() {
                    infowindow.setContent(getStaticContentString(data[station]));

                    //gets the number of irfs
                    $.get("/portal/get_interception_records", {station_code: data[station].fields.station_code}, function(data){
                        $("#stationInterception").text("Interceptions: " + data);
                    });

                    //gets the number of staff
                    $.get("/portal/get_staff_count", {station_code: data[station].fields.station_code}, function(data){
                        $("#staffset").text('# of Staff:' + data);
                    });

                    if(!marker.clicked) {
                        infowindow.open(map, this);
                    }

                    $(".gm-style-iw").each(function() { // TODO: We are resizing according to the length of the station name? we need a better solution for this!
                        if(data[station].fields.station_name.length > 10) {
                            $(this).addClass('station-info-window-big');
                        }
                        $(this).addClass('station-info-window');
                    });
                }
            })(marker, station));

            google.maps.event.addListener(marker, 'click', (function(marker, station) { //For the Dynamic view
                return function() {
                    infowindow.close();
                    marker.clicked = true;

                    dynamicWindow.setContent(getDynamicContentString(data[station]));

                    //gets the number of IRFs to date
                    $.get("/portal/get_interception_records", {station_code: data[station].fields.station_code}, function(data){
                        $("#stationInterception").text("Interceptions: " + data);
                    });

                    //gets the number of staff
                    $.get("/portal/get_staff_count", {station_code: data[station].fields.station_code}, function(data){
                        $("#staffset").text('# of Staff:' + data);
                    });


                    dynamicWindow.open(map, this);

                    $(".gm-style-iw").each(function() {
                        if(data[station].fields.station_name.length > 10) {
                            $(this).addClass('station-info-window-big-dynamic');
                        }
                        $(this).addClass('station-info-window-big-dynamic');

                    });
                }
            })(marker, station));

            function toggleMarkerClick(marker){
                marker.clicked = false;
            }
        }
    });
}

function hasShelter(borderStation){ // basically just converts a true/false to a yes/no
    if(borderStation.fields.has_shelter) {
        return "Yes";
    }
    else {
        return "No";
    }
}

$( window ).resize(function() {
  resizeMap();
});

$(function() {
    google.maps.event.addDomListener(window, 'load', initialize);
    resizeMap();
});