angular
    .module('DataEntry')
    .factory('irfService', irfService);

irfService.$inject = ['$http'];

function irfService($http) {
	return {
		listIrfs: listIrfs
	};

	function listIrfs() {
        return $http.get('/api/irf/').
            success(function (data) {
                return data;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }
}