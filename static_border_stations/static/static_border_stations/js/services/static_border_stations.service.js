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
			getDetails: getDetails,
			updateCommitteeMembers: updateCommitteeMembers,
			updateLocations: updateLocations,
			updateStaff: updateStaff,
			updateDetails: updateDetails
		};
	
		function getDetails(borderStationId) {
			return $http.get('/api/border-stations/' + borderStationId);
		}
	
		function getStaff(borderStationId) {
			return $http.get('/api/staff/?border_station=' + borderStationId);
		}
	
		function getCommitteeMembers(borderStationId) {
			return $http.get('/api/committee-members/?border_station=' + borderStationId);
		}
	
		function getLocations(borderStationId) {
			return $http.get('/api/locations/?border_station=' + borderStationId);
		}
	
		function updateDetails(borderStationId, data) {
			return $http.put('/api/border-stations/' + borderStationId, data);
		}
	
		function updateStaff(staffId, data) {
			return $http.put('/api/staff/' + staffId, data);
		}
	
		function updateCommitteeMembers(memberId, data) {
			return $http.put('/api/committee-members/' + memberId, data);
		}
	
		function updateLocations(locationId, data) {
			return $http.put('/api/locations/' + locationId, data);
		}
	}
})();