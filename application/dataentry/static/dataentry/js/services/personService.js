'use strict';

angular
    .module('DataEntry')
    .factory('personService', personService);

personService.$inject = ['$http'];

function personService($http) {
	return {
		listPersons: listPersons,
		searchPersons: searchPersons,
		loadMorePersons: loadMorePersons,
		saveAddress: saveAddress,
    getForm: getForm
	};

  function listPersons(queryParams){
        return $http.get('/api/person/' + queryParams)
            .success(function (data) {
                return data;
            })
            .error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
  }

	function searchPersons(queryParams) {
        return listPersons(queryParams);
  }

  function getForm(person) {
        return("Hello")
  }

	function loadMorePersons(url, queryParams) {
        return $http.get(url + queryParams).
            success(function (data) {
                return data;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
  }

	function saveAddress(person) {
        return $http.put('/api/person/' + person.id + '/', person).
            success(function (data) {
                return data;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
  }
}
