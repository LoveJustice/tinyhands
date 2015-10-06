(function() {
	'use strict';
	
	angular.module('BorderStationsMod')
		.factory('BorderStationsService', BorderStationsService);
		
	BorderStationsService.$inject = ['$http'];
		
	function BorderStationsService($http) {
		return {
			getCommitteeMembers: getCommitteeMembers,
			getLocations: getLocations,
			getStaff: getStaff,
			getStation: getStation
		};
	
		function getStation(borderStationId) {
			return $http.get('/api/border-stations/' + borderStationId);
		}
	
		function getStaff(borderStationId) {
			return $http.get('/api/staff/?borderstation=' + borderStationId);
		}
	
		function getCommitteeMembers(borderStationId) {
			return $http.get('/api/committee-members/?borderstation=' + borderStationId);
		}
	
		function getLocations(borderStationId) {
			return $http.get('/api/locations/?borderstation=' + borderStationId);
		}
	}
})();