'use strict';

angular
    .module('DataEntry')
    .factory('address2Service', address2Service);

address2Service.$inject = ['$http'];

function address2Service($http) {
	return {
		listAddresses: listAddresses,
		searchAddresses: searchAddresses,
		loadMoreAddresses: loadMoreAddresses
	};

	function listAddresses(pageSize) {
        // grab all of the staff for this budgetCalcSheet
        return $http.get('/api/address2/' + '?page_size=' + pageSize).
            success(function (data) {
                return data;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }

	function searchAddresses(searchValue) {
        // grab all of the staff for this budgetCalcSheet
        if(!searchValue){
            searchValue = "empty";
        }
        return $http.get('/api/address2/search/' + searchValue + '/').
            success(function (data) {
                return data;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }

	function loadMoreAddresses(url, pageSize) {
        // grab all of the staff for this budgetCalcSheet
        return $http.get(url + '&page_size=' + pageSize).
            success(function (data) {
                return data;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }
}