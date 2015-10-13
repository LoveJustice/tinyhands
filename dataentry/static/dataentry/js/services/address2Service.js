'use strict';

angular
    .module('DataEntry')
    .factory('address2Service', address2Service);

address2Service.$inject = ['$http'];

function address2Service($http) {
	return {
		listAddresses: listAddresses,
		listAddress1s: listAddress1s,
		searchAddresses: searchAddresses,
		loadMoreAddresses: loadMoreAddresses,
		saveAddress: saveAddress
	};

	function listAddresses(queryParams) {
        return $http.get('/api/address2/' + queryParams).
            success(function (data) {
                return data;
            }).
            error(function (data, status, headers, config) {
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
        return $http.put('/api/address2/' + address.id, address).
            success(function (data) {
                return data;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }

    function listAddress1s(){
        return $http.get('/api/address1/')
            .success(function (data) {
                return data;
            })
            .error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }
}