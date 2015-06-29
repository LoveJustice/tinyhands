angular
    .module('DataEntry')
    .factory('staffListService', staffListService);

staffListService.$inject = ['$http', '$q'];

function staffListService($http, $q) {
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