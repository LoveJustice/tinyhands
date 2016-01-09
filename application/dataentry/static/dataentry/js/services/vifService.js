angular
    .module('DataEntry')
    .factory('vifService', vifService);

vifService.$inject = ['$http'];

function vifService($http) {
	return {
		listVifs: listVifs,
		loadMoreVifs: loadMoreVifs,
		deleteVif: deleteVif
	};

	function listVifs(queryparams) {
        return $http.get('/api/vif/' + queryparams).
            success(function (data) {
                return data;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }

    function loadMoreVifs(url, queryparams){
        return $http.get(url + queryparams).
            success(function (data) {
                return data;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }

    function deleteVif(url){
        return $http.delete(url)
            .success(function(status){
                return status;
            })
            .error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });

    }

}