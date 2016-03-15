'use strict';

angular
    .module('DataEntry')
    .factory('address1Service', address1Service);

address1Service.$inject = ['$http'];

function address1Service($http) {
	return {
		listAddresses: listAddresses,
		searchAddresses: searchAddresses,
		loadMoreAddresses: loadMoreAddresses,
		saveAddress: saveAddress
	};

    function listAddresses(queryParams){
        return $http.get('/api/address1/' + queryParams)
            .success(function (data) {
                return data;
            })
            .error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }

	function searchAddresses(queryParams) {
        return listAddresses(queryParams);
    }

	function loadMoreAddresses(url, queryParams) {
        return $http.get(url + queryParams).
            success(function (data) {
                return data;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }

	function saveAddress(address) {
        return $http.put('/api/address1/' + address.id, address).
            success(function (data) {
                return data;
            }).
            error(function (data, status, headers, config) {
            });
    }
}
