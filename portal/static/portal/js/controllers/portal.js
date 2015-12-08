(function() {
    'use strict';

    angular.module('PortalMod')
       .controller('MapCtrl', MapCtrl);

    MapCtrl.$inject = ['$rootScope'];

    function MapCtrl($rootScope) {
        var vm = this;

        vm.VDCLayer = null;
        vm.map = null;

        vm.toggleVDCLayer = toggleVDCLayer;

        function activate() {
            var mapOptions = {
              center: { lat: 28.394857, lng: 84.124008},
              zoom: 8,
              streetViewControl: false
            };

            vm.VDCLayer = new google.maps.FusionTablesLayer({
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

            vm.map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

            getBorderStations(vm.map);
            vm.VDCLayer.setMap(vm.map);

            $( window ).resize(function() {
                resizeMap();
            });

            $rootScope.$on('toggleVDCLayer', toggleVDCLayer);
        }

        function toggleVDCLayer(event, hide) {
            if(!hide) {
                vm.VDCLayer.setMap(null);
            }
            else {
                vm.VDCLayer.setMap(vm.map);
            }
        }

        function resizeMap() {
            var map_canvas = document.getElementById('map-canvas');
            map_canvas.style.width = window.innerWidth+"px";
            map_canvas.style.height = (window.innerHeight-50)+"px";
        }

        function getStaticContentString(borderStation) { //This is what the content of a static border_station is
          return '<div id="Static'+borderStation.fields.station_code+'" class="dashboardInfoWindow">' +
            '<h3>' + borderStation.fields.station_name + ' - ' + borderStation.fields.station_code + '</h3>' +

            '<p>Est. ' + established(borderStation) + '</p>' +
            '<p id="shelter">Has shelter: ' + hasShelter(borderStation) + '</p>' +
            '<p id="stationInterception">Interceptions: ' + '</p>' +
            '<p id="staffset"># of Staff ' + '</p>' +
            '</div>';
        }

        function getDynamicContentString(borderStation){ //This is what the content of a static border_station is
            return '<div id="Dynamic'+borderStation.fields.station_code+'" class="dynamicInfoWindow">' +
                '<h3>' + borderStation.fields.station_name + ' - ' + borderStation.fields.station_code + '</h3>' +
                '<div id="leftColumn" class="col-md-6">'+


                    '<p>Est. ' + established(borderStation) + '</p>' +
                    '<p id="shelter">Has shelter: ' + hasShelter(borderStation) + '</p>' +
                    '<p id="stationInterception"></p>' +
                    '<p id="staffset"># of Staff ' + '</p>' +
                '</div>'+

                '<div id="rightColumn" class="col-md-6">'+
                    '<p id="BS"><a href="/static_border_stations/border-stations/' + borderStation.pk + '">Subcommittee, Staff, and Locations</a>' + '</p>' +
                    '<p id="irf"><a href="/data-entry/irfs/search/' + borderStation.fields.station_code + '">IRFs</a>' + '</p>' +
                    '<p id="vif"><a href="/data-entry/vifs/search/' + borderStation.fields.station_code + '">VIFs</a>' + '</p>' +
                '</div>'+
            '</div>';
        }

        function getBorderStations(map){
            /*  Runs on page load to show all the border stations on the
             *  map and set all of the onClick/onHover events for them
             */
            $.get("/portal/get_border_stations",function(data, status){
                var infoWindow = new google.maps.InfoWindow(); //Initialize the Static Border Station view

                var dynamicWindow = new google.maps.InfoWindow(); //Initialize the Dynamic Border Station view


                for(var station=0;station<data.length;station++) { //Iterate over each Border Station
                  if (data[station].fields.open == true) {
                    var myLatlng = new google.maps.LatLng(data[station].fields.latitude, data[station].fields.longitude);
                    var marker = new google.maps.Marker({ //Initialize a BorderStation's marker
                      position: myLatlng,
                      map: map,
                      title: data[station].fields.station_name + " " + data[station].fields.station_code,
                      clicked: false,
                      optimized: false
                    });

                    // Create Listeners
                    createCloseWindowListener(dynamicWindow, marker);

                    createMouseOutWindowListener(infoWindow, marker, station);

                    createMouseOverWindowListener(infoWindow, marker, station, data, map);

                    createClickWindowListener(dynamicWindow, infoWindow, marker, station, data, map);
                  }
                }
            });
        }

        function createCloseWindowListener(dynamicWindow, marker) {
            google.maps.event.addListener(dynamicWindow, 'closeclick', (function(marker) {
                return function() {
                    toggleMarkerClick(marker);
                }
            })(marker));
        }

        function createMouseOutWindowListener(infoWindow, marker, station) {
            google.maps.event.addListener(marker, 'mouseout', (function(marker, station) {
                return function() {
                    infoWindow.close();
                    $(".gm-style-iw").each(function() {
                        $(this).removeClass('station-info-window');
                    });
                }
            })(marker, station));
        }

        function createMouseOverWindowListener(infoWindow, marker, station, data, map) {
            google.maps.event.addListener(marker, 'mouseover', (function(marker, station) { //For the Static View
                return function() {
                    infoWindow.setContent(getStaticContentString(data[station]));

                    if(!marker.clicked) {
                        infoWindow.open(map, this);
                    }

                    getMarkerDataOnHoverOrClick(data,station);

                    $(".gm-style-iw").each(function() { // TODO: We are resizing according to the length of the station name? we need a better solution for this!
                        if(data[station].fields.station_name.length > 10) {
                            $(this).addClass('station-info-window-big');
                        }
                        $(this).addClass('station-info-window');
                    });
                }
            })(marker, station));
        }

        function createClickWindowListener(dynamicWindow, infoWindow, marker, station, data, map) {
            google.maps.event.addListener(marker, 'click', (function(marker, station) { //For the Dynamic view
                return function() {
                    infoWindow.close();
                    marker.clicked = true;

                    dynamicWindow.setContent(getDynamicContentString(data[station]));

                    getMarkerDataOnHoverOrClick(data,station);

                    dynamicWindow.open(map, this);

                    $(".gm-style-iw").each(function() {
                        if(data[station].fields.station_name.length > 10) {
                            $(this).addClass('station-info-window-big-dynamic');
                        }
                        $(this).addClass('station-info-window-big-dynamic');

                    });
                }
            })(marker, station));
        }

        function getMarkerDataOnHoverOrClick(data, station) {
            //gets the number of irfs
            $.get("/portal/get_interception_records", {station_code: data[station].fields.station_code}, function(data){
                $("#stationInterception").text("Interceptions: " + data);
            });

            //gets the number of staff
            $.get("/portal/get_staff_count", {station_code: data[station].fields.station_code}, function(data){
                $("#staffset").text('# of Staff: ' + data);
            });
        }

        function toggleMarkerClick(marker){
            marker.clicked = false;
        }

        function hasShelter(borderStation){ // basically just converts a true/false to a yes/no
            if(borderStation.fields.has_shelter) {
                return "Yes";
            }
            else {
                return "No";
            }
        }

        function established(borderStation){
            if (borderStation.fields.date_established === null){
                return "Unknown";
            } else {
                return borderStation.fields.date_established;
            }
        }

        /*
         * The map must know the size of the div before rendering.
         * Having this here ensures everything is ready before activation.
         * Sauce (http://stackoverflow.com/questions/4700594/google-maps-displaynone-problem)
         * -- Justin Southworth
         */
        google.maps.event.addDomListener(window, 'load', activate);
    };
})();
