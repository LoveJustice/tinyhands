angular
    .module('DataEntry')
    .factory('irfService', irfService);

irfService.$inject = ['$http'];

function irfService($http) {
	return {
		listIrfs: listIrfs,
		loadMoreIrfs: loadMoreIrfs,
		deleteIrf: deleteIrf,
        batchIrf: batchIrf
	};

	function listIrfs(queryparams) {
        return $http.get('/api/irf/' + queryparams).
            success(function (data) {
                return data;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }

    function loadMoreIrfs(url, queryparams){
        return $http.get(url + queryparams).
            success(function (data) {
                return data;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }

    function deleteIrf(url){
        return $http.delete(url).
            success(function(status){
                return status;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });

    }

    function batchIrf(startDate, endDate) {
        return $http.get('/data-entry/batch/' + startDate +'/' + endDate).
            success(function (data) {
                return data;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }
}