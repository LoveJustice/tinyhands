angular
    .module('DataEntry')
    .factory('borderStationService', borderStationService);

borderStationService.$inject = ['$http'];

function borderStationService($http) {
	return {
		retrieveStaff: retrieveStaff,
        retrieveLocations: retrieveLocations,
		getStationID: getStationID
	};

	function retrieveStaff(borderStationCod) {
        // grab all of the staff for this station
        return $http.get('/api/staff/' + borderStationCod + '/').
            success(function (data) {
                console.log("staff data",data);
                return data;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }
    
    function retrieveLocations(borderStationCod) {
        // grab all of the locations for this station
        return $http.get('/api/location/' + borderStationCod + '/').
            success(function (data) {
                console.log("location data",data);
                return data;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }

    function getStationID(borderStationCod) {
        return $.get( '/api/get_station_id/', {"code": borderStationCod}).
            success(function(data) {
                return data;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });

    }

}