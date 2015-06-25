angular
    .module('DataEntry')
    .factory('staffListService', staffListService);

staffListService.$inject = ['$http', '$q'];

function staffListService($http, $q) {
	return {
		retrieveStaff: retrieveStaff
	};

	function retrieveStaff(borderStationCod) {
        // grab all of the staff for this budgetCalcSheet
        borderStationId = BorderStation.objects.get(station_code=borderStationCod).id
        return $http.get('/static_border_stations/api/border-stations/' + borderStationId + '/').
            success(function (data) {
                return data;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }

}