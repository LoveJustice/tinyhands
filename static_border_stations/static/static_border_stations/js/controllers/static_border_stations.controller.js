(function() {
	'use strict';
	
	angular.module('BorderStationsMod')
		.controller('BorderStationsCtrl', BorderStationsCtrl);
		
	BorderStationsCtrl.$inject = ['$q','$timeout','BorderStationsService'];
		
	function BorderStationsCtrl($q, $timeout, BorderStationsService) {
		var vm = this;
		
		var committeeMemTitle = 'Committee Members';
		var staffTitle = 'Staff';
		var updateButtonText = 'Update Station';
		
		vm.addLocation = addLocation;
		vm.addPerson = addPerson;
		vm.borderStationId = window.border_station_pk;
		vm.changeStationStatus = changeStationStatus;
		vm.details = {};
		vm.errors = [];
		vm.locations = [];
		vm.newCommitteeMembers = [];
		vm.newLocations = [];
		vm.newStaff = [];
		vm.people = {
			staff: {
				name: staffTitle
			},
			committeeMembers: {
				name: committeeMemTitle
			}
		};
		vm.removeLocation = removeLocation;
		vm.removePerson = removePerson;
		vm.updateStation = updateStation;
		vm.updateStatusText = updateButtonText;
		
		activate();
		
		function activate() {
			getDetails();
			getStaff();
			getCommitteeMembers();
			getLocations();
		}
		
		function handleErrors(error) {
			var errorData = error.data;
			for (var key in errorData) {
				vm.errors.push({
					field: key,
					messages: errorData[key]
				});
			}
		}
		
		function addLocation() {
			var newLocation = {
				border_station: vm.borderStationId
			};
			vm.newLocations.push(newLocation);
			vm.locations.push(newLocation);
		}
		
		function addPerson(persons) {
			var newPerson = {
				border_station: vm.borderStationId
			};
			if (persons.name == staffTitle) {
				vm.newStaff.push(newPerson);
				vm.people.staff.data.push(newPerson);
			} else if (persons.name == committeeMemTitle) {
				vm.newCommitteeMembers.push(newPerson);
				vm.people.committeeMembers.data.push(newPerson);
			}
		}
		
		function changeStationStatus() {
			vm.details.open = !vm.details.open;
		}
		
		
		// CREATE calls
		function createCommitteeMembers(members) {
			var defered = $q.defer();
			createRelationship(members, BorderStationsService.createCommitteeMember, getCommitteeMembers).then(function() {
				vm.newCommitteeMembers = []; // Empty the array after all of the create calls have been fired.
				defered.resolve('Finished creating Committee Members');
			});
			return defered.promise;
		}
		
		function createLocations(locations) {
			var defered = $q.defer();
			createRelationship(locations, BorderStationsService.createLocation, getLocations).then(function() {
				vm.newLocations = []; // Empty the array after all of the create calls have been fired.
				defered.resolve('Finished creating Locations');
			});
			return defered.promise;
		}
		
		function createStaff(staff) {
			var defered = $q.defer();
			createRelationship(staff, BorderStationsService.createStaff, getStaff).then(function() {
				vm.newStaff = []; // Empty the array after all of the create calls have been fired.
				defered.resolve('Finished creating Staff');
			});
			return defered.promise;
		}
		
		function createRelationship(createArray, createApiFunction, getApiFunction) {
			var expectedNumCalls = createArray.length;
			var numCalls = 0;
			var defered = $q.defer();
			createArray.forEach(function (anObject) {
				createApiFunction(anObject).then(function() {
					getApiFunction();
					numCalls++;
					if (numCalls >= expectedNumCalls) {
						defered.resolve('Finished sending create calls');
					}
				}, handleErrors);
			});
			
			if (expectedNumCalls == 0) {
				defered.resolve('No create calls needed');
			}
			
			return defered.promise;
		}
		
		
		// GET calls
		function getDetails() {
			if (vm.borderStationId) {
				BorderStationsService.getDetails(vm.borderStationId).then(function(response) {
					vm.details = response.data;
				}, handleErrors);
			}
		}
		
		function getCommitteeMembers() {
			if (vm.borderStationId) {
				BorderStationsService.getCommitteeMembers(vm.borderStationId).then(function(response) {
					vm.people.committeeMembers.data = response.data.results;
				}, handleErrors);
			}
		}
		
		function getLocations() {
			if (vm.borderStationId) {
				BorderStationsService.getLocations(vm.borderStationId).then(function(response) {
					vm.locations = response.data.results;
				}, handleErrors);
			}
		}
		
		function getStaff() {
			if (vm.borderStationId) {
				BorderStationsService.getStaff(vm.borderStationId).then(function(response) {
					vm.people.staff.data = response.data.results;
				}, handleErrors);
			}
		}
		
		
		// REMOVE calls
		function removeCommitteeMember(member) {
			removeRelation(member, vm.newCommitteeMembers, vm.people.committeeMembers.data, BorderStationsService.updateCommitteeMembers, getCommitteeMembers);
		}
		
		function removeLocation(location) {
			if (location.removeConfirmed) {
				removeRelation(location, vm.newLocations, vm.locations, BorderStationsService.updateLocations, getLocations);
			} else {
				location.removeConfirmed = true;
			}
		}
		
		function removePerson(persons, person) {
			if (person.removeConfirmed) {
				persons.name == staffTitle ? removeStaff(person) : removeCommitteeMember(person);
			} else {
				person.removeConfirmed = true;
			}
		}
		
		function removeRelation(value, newArray, currentArray, updateApiFunction, getApiFunction) {
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
					}, handleErrors);
				}
			}
		}
		
		function removeStaff(staff) {
			removeRelation(staff, vm.newStaff, vm.people.staff.data, BorderStationsService.updateStaff, getStaff);
		}
		
		
		// UPDATE calls
		function updateCommitteeMembers(committeeMembers) {
			var defered = $q.defer();
			updateRelationship(committeeMembers, BorderStationsService.updateCommitteeMembers, getCommitteeMembers, vm.newCommitteeMembers.length).then(function() {
				defered.resolve('Finished updating Committee Members');
			});
			return defered.promise;
		}
		
		function updateDetails(details) {
			// Format date properly
			var dateEstablished = new Date(details.date_established);
			var year = dateEstablished.getFullYear();
			var month = dateEstablished.getMonth() + 1; // Plus 1 because it returns 0 - 11 inclusive to rep month
			var day = dateEstablished.getDate();
			var dateString = year.toString();
			if (month) {
				dateString += '-' + month;
				if (day) {
					dateString += '-' + day;
				}
			}
			details.date_established = dateString;
			
			var defered = $q.defer();
			
			updateRelationship([details], BorderStationsService.updateDetails, getDetails).then(function() {
				defered.resolve('Finished updating Details');
			});
			return defered.promise;
		}
		
		function updateLocations(locations) {
			var defered = $q.defer();
			updateRelationship(locations, BorderStationsService.updateLocations, getLocations, vm.newLocations.length).then(function() {
				defered.resolve('Finished updating Locations');
			});
			return defered.promise;
		}
		
		function updateStaff(staff) {
			var defered = $q.defer();
			updateRelationship(staff, BorderStationsService.updateStaff, getStaff, vm.newStaff.length).then(function() {
				defered.resolve('Finished updating Staff');
			});
			return defered.promise;
		}
		
		function updateRelationship(updateArray, updateApiFunction, getApiFunction, numNew) {
  		numNew = typeof numNew !== 'undefined' ? numNew : 0; // if null then set to 0
			var expectedNumCalls = updateArray.length - numNew;
			var numCalls = 0;
			var defered = $q.defer();
			updateArray.forEach(function(anObject) {
				if (anObject.id) {
					updateApiFunction(anObject.id, anObject).then(function() {
						getApiFunction();
						numCalls++;
						if (numCalls >= expectedNumCalls) {
							defered.resolve('Finished sending update calls');
						}
					}, handleErrors);
				}
			});
			
			if (expectedNumCalls == 0) {
				defered.resolve('No update calls needed');
			}
			
			return defered.promise
		}
		
		function updateStation() {
			vm.updateStatusText = 'Saving...';
			
			var promises = [];
			
			promises.push(createCommitteeMembers(vm.newCommitteeMembers));
			promises.push(createLocations(vm.newLocations));
			promises.push(createStaff(vm.newStaff));
			
			promises.push(updateDetails(vm.details));
			promises.push(updateCommitteeMembers(vm.people.committeeMembers.data));
			promises.push(updateLocations(vm.locations));
			promises.push(updateStaff(vm.people.staff.data));
			
			
			$q.all(promises).then(function() {
				vm.updateStatusText = 'Saved';
				$timeout(function() {
					vm.updateStatusText = updateButtonText;
				}, 2000);
			});
		}
	}
})();