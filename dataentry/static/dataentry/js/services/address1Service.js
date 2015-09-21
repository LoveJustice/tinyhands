angular
    .module('DataEntry')
    .factory('address1Service', address1Service);

address1Service.$inject = ['$http'];

function address1Service($http) {
	return {
		retrieveStaff: retrieveStaff,
		getStationID: getStationID,
	};

	function retrieveStaff(borderStationCod) {
        // grab all of the staff for this budgetCalcSheet
        return $http.get('/static_border_stations/api/border-stations/' + borderStationCod + '/').
            success(function (data) {
                return data;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }

    function getStationID(borderStationCod) {
        return $.get( '/get_station_id/', {"code": borderStationCod}).
            success(function(data) {
                station_id = data;
                return station_id;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });

    }

}