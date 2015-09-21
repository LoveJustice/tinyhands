'use strict';

angular
    .module('DataEntry')
    .factory('address2Service', address2Service);

address2Service.$inject = ['$http'];

function address2Service($http) {
	return {
		listAddresses: listAddresses,
		searchAddresses: searchAddresses
	};

	function listAddresses() {
        // grab all of the staff for this budgetCalcSheet
        return $http.get('/api/address2/').
            success(function (data) {
                return data;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }

	function searchAddresses(searchValue) {
        // grab all of the staff for this budgetCalcSheet
        return $http.get('/api/address2/search/' + searchValue + '/').
            success(function (data) {
                return data;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }
}