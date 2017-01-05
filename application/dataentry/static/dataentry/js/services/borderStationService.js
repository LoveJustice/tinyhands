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
                return data;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }
    
    function retrieveLocations(borderStationCode) {
        // grab all of the locations for this station
        return $http.get('/api/location/' + borderStationCode + '/').
            success(function (data) {
                return data;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }

    function getStationID(borderStationCode) {
        return $.get( '/api/get_station_id/', {"code": borderStationCode}).
            success(function(data) {
                return data;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });

    }

}