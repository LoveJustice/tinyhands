(function() {
	'use strict';
	
	angular.module('BorderStationsMod')
		.factory('BorderStationsService', BorderStationsService);
		
	BorderStationsService.$inject = ['$http'];
		
	function BorderStationsService($http) {
		return {
			getStation: getStation
		};
	
		function getStation(borderStationId) {
			return $http.get('/api/border-stations/' + borderStationId + '/')
									.error(function (data, status, headers, config) {
											console.log(data, status, headers, config);
									});
		}
	}
})();