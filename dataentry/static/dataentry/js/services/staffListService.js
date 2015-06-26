angular
    .module('DataEntry')
    .factory('staffListService', staffListService);

staffListService.$inject = ['$http', '$q'];

function staffListService($http, $q) {
	return {
		retrieveStaff: retrieveStaff
	};

	function retrieveStaff(borderStationCod) {
	    /*
        $.getJSON('/stations/ids/'+borderStationCod+'/', function(data, jqXHR){
            console.log("calling my function");
            var test = data[0].id;
            console.log(test);
            stationID = test;
        });
        */
        // grab all of the staff for this budgetCalcSheet
        return $http.get('/static_border_stations/api/border-stations/' + borderStationCod + '/').
            success(function (data) {
                return data;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }

    function getStationID(borderStationCod) {
        var borderID = $http({method: 'GET', url: '/dataentry/api/border_stations/' + borderStationCod + '/'});
        return $q.all([borderID])
            .then(function (data) {
                return data;
            })
            .catch(function(data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }

}