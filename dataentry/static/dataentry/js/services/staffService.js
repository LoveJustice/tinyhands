angular
    .module('DataEntry')
    .factory('staffService', staffService);

staffService.$inject = ['$http', '$q'];

function staffService($http, $q) {
	return {
		retrieveStaff: retrieveStaff
	};

	function retrieveStaff(borderStationId) {
        // grab all of the staff for this budgetCalcSheet
        return $http.get('/static_border_stations/api/border-stations/' + borderStationId + '/').
            success(function (data) {
                return data;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }

}