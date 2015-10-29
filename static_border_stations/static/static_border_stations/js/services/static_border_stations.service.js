(function() {
	'use strict';
	
	angular.module('BorderStationsMod')
		.factory('BorderStationsService', BorderStationsService);
		
	BorderStationsService.$inject = ['$http','$q'];
		
	function BorderStationsService($http, $q) {
		return {
			createCommitteeMember: createCommitteeMember,
			createLocation: createLocation,
			createRelationship: createRelationship,
			createStaff: createStaff,
			getCommitteeMembers: getCommitteeMembers,
			getDetails: getDetails,
			getLocations: getLocations,
			getStaff: getStaff,
			removeRelationship: removeRelationship,
			updateCommitteeMembers: updateCommitteeMembers,
			updateDetails: updateDetails,
			updateLocations: updateLocations,
			updateRelationship: updateRelationship,
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
		
		function createRelationship(createArray, createApiFunction, errorHandler) {
			var expectedNumCalls = createArray.length;
			var numCalls = 0;
			var deferred = $q.defer();
			createArray.forEach(function (anObject) {
				createApiFunction(anObject).then(function() {
					numCalls++;
					if (numCalls >= expectedNumCalls) {
						deferred.resolve('Finished sending create calls');
					}
				}, function(error) {
					deferred.reject(error);
					errorHandler(error);
				});
			});
			
			if (expectedNumCalls == 0) {
				deferred.resolve('No create calls needed');
			}
			
			return deferred.promise;
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
		
		
		// REMOVE
		function removeRelationship(value, newArray, currentArray, updateApiFunction, getApiFunction, errorHandler) {
			var idx = newArray.indexOf(value);
			if (idx >= 0) { // If relation was just created and isnt (shouldnt be) in the db
				newArray.splice(idx, 1);
				
				// Remove item from list
				idx = currentArray.indexOf(value);
				currentArray.splice(idx, 1);
			} else { // If exists in db
				value.border_station = null;
				if (value.id) {
					updateApiFunction(value.id, value).then(function() {
						getApiFunction();
					}, errorHandler);
				}
			}
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
		
		function updateRelationship(updateArray, updateApiFunction, numNew, errorHandler) {
  		numNew = typeof numNew !== 'undefined' ? numNew : 0; // if null then set to 0
			var expectedNumCalls = updateArray.length - numNew;
			var numCalls = 0;
			var deferred = $q.defer();
			updateArray.forEach(function(anObject) {
				if (anObject.id) {
					updateApiFunction(anObject.id, anObject).then(function() {
						numCalls++;
						if (numCalls >= expectedNumCalls) {
							deferred.resolve('Finished sending update calls');
						}
					}, function(error) {
						deferred.reject(error);
						errorHandler(error);
					});
				}
			});
			
			if (expectedNumCalls == 0) {
				deferred.resolve('No update calls needed');
			}
			
			return deferred.promise
		}
	
		function updateStaff(staffId, data) {
			return $http.put('/api/staff/' + staffId, data);
		}
	}
})();