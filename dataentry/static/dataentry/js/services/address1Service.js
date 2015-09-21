angular
    .module('DataEntry')
    .factory('address1Service', address1Service);

address1Service.$inject = ['$http'];

function address1Service($http) {
	return {
		retrieveStaff: retrieveAddress2,
	};


	function retrieveAddress2() {
        // grab all of the staff for this budgetCalcSheet
        return $http.get('/static_border_stations/api/border-stations/' + borderStationCod + '/').
            success(function (data) {
                return data;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }

}