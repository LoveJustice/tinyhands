(function() {
	'use strict';
	
	angular.module('BorderStationsMod')
		.factory('BorderStationsService', BorderStationsService);
		
	BorderStationsService.$inject = ['$http'];
		
	function BorderStationsService($http) {
		return {
			createCommitteeMember: createCommitteeMember,
			createLocation: createLocation,
			createStaff: createStaff,
			getCommitteeMembers: getCommitteeMembers,
			getDetails: getDetails,
			getLocations: getLocations,
			getStaff: getStaff,
			updateCommitteeMembers: updateCommitteeMembers,
			updateDetails: updateDetails,
			updateLocations: updateLocations,
			updateStaff: updateStaff
		};
	
	
		// POSTs
		function createCommitteeMember(data) {
			return $http.post('/api/committee-members/', data);
		}
	
		function createLocation(data) {
			return $http.post('/api/locations/', data);
		}
	
		function createStaff(data) {
			return $http.post('/api/staff/', data);
		}
	
		
		// GETs
		function getCommitteeMembers(borderStationId) {
			return $http.get('/api/committee-members/?border_station=' + borderStationId);
		}
	
		function getDetails(borderStationId) {
			return $http.get('/api/border-stations/' + borderStationId);
		}
	
		function getLocations(borderStationId) {
			return $http.get('/api/locations/?border_station=' + borderStationId);
		}
	
		function getStaff(borderStationId) {
			return $http.get('/api/staff/?border_station=' + borderStationId);
		}
	
	
		// PUTs
		function updateCommitteeMembers(memberId, data) {
			return $http.put('/api/committee-members/' + memberId, data);
		}
	
		function updateDetails(borderStationId, data) {
			return $http.put('/api/border-stations/' + borderStationId, data);
		}
	
		function updateLocations(locationId, data) {
			return $http.put('/api/locations/' + locationId, data);
		}
	
		function updateStaff(staffId, data) {
			return $http.put('/api/staff/' + staffId, data);
		}
	}
})();