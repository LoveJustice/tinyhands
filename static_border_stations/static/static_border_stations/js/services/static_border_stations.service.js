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
			return $http.get('/api/border-stations/' + borderStationId + '/');
		}
	
		function getStaff(borderStationId) {
			return $http.get('/api/staff/' + borderStationId + '/');
		}
	
		function getCommitteeMembers(borderStationId) {
			return $http.get('/api/committee-members/' + borderStationId + '/');
		}
	
		function getLocations(borderStationId) {
			return $http.get('/api/locations/' + borderStationId + '/');
		}
	}
})();