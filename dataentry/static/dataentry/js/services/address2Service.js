'use strict';

angular
    .module('DataEntry')
    .factory('address2Service', address2Service);

address2Service.$inject = ['$http'];

function address2Service($http) {
	return {
		listAddresses: listAddresses,
		searchAddresses: searchAddresses,
		loadMoreAddresses: loadMoreAddresses,
		saveAddress: saveAddress
	};

	function listAddresses(pageSize) {
        return $http.get('/api/address2/' + '?page_size=' + pageSize).
            success(function (data) {
                return data;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }

	function searchAddresses(pageSize, searchValue, ordering) {
        if(!searchValue){
            searchValue = "empty";
        }
        return $http.get('/api/address2/?search=' + searchValue + '&page_size=' + pageSize + '&ordering=' + ordering).
            success(function (data) {
                return data;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }

	function loadMoreAddresses(url, pageSize) {
        return $http.get(url + '&page_size=' + pageSize).
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