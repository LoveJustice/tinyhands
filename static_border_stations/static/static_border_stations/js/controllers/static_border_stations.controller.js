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
		vm.createRelationship = createRelationship;
		vm.details = {};
		vm.errors = [];
		vm.handleErrors = handleErrors;
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
		vm.removeRelationship = removeRelationship;
		vm.updateRelationship = updateRelationship;
		vm.updateStation = updateStation;
		vm.updateStatusText = updateButtonText;
		
		activate();
		
		function activate() {
			getData();
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
			vm.createRelationship(members, BorderStationsService.createCommitteeMember).then(function() {
				vm.newCommitteeMembers = []; // Empty the array after all of the create calls have been fired.
				defered.resolve('Finished creating Committee Members');
			}, function(error) {
				defered.reject(error);
			});
			return defered.promise;
		}
		
		function createLocations(locations) {
			var defered = $q.defer();
			vm.createRelationship(locations, BorderStationsService.createLocation).then(function() {
				vm.newLocations = []; // Empty the array after all of the create calls have been fired.
				defered.resolve('Finished creating Locations');
			}, function(error) {
				defered.reject(error);
			});
			return defered.promise;
		}
		
		function createRelationship(createArray, createApiFunction) {
			return BorderStationsService.createRelationship(createArray, createApiFunction, vm.handleErrors);
		}
		
		function createStaff(staff) {
			var defered = $q.defer();
			vm.createRelationship(staff, BorderStationsService.createStaff).then(function() {
				vm.newStaff = []; // Empty the array after all of the create calls have been fired.
				defered.resolve('Finished creating Staff');
			}, function(error) {
				defered.reject(error);
			});
			return defered.promise;
		}
		
		
		// GET calls
		function getData() {
			getDetails();
			getStaff();
			getCommitteeMembers();
			getLocations();
		}
		
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
		
		
		// Error Handling
		function handleErrors(error) {
			var errorData = error.data;
			for (var key in errorData) {
				vm.errors.push({
					field: key,
					messages: errorData[key]
				});
			}
		}
		
		
		// REMOVE calls
		function removeCommitteeMember(member) {
			vm.removeRelationship(member, vm.newCommitteeMembers, vm.people.committeeMembers.data, BorderStationsService.updateCommitteeMembers, getCommitteeMembers);
		}
		
		function removeLocation(location) {
			if (location.removeConfirmed) {
				vm.removeRelationship(location, vm.newLocations, vm.locations, BorderStationsService.updateLocations, getLocations);
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
		
		function removeRelationship(value, newArray, currentArray, updateApiFunction, getApiFunction) {
			BorderStationsService.removeRelationship(value, newArray, currentArray, updateApiFunction, getApiFunction, vm.handleErrors);
		}
		
		function removeStaff(staff) {
			vm.removeRelationship(staff, vm.newStaff, vm.people.staff.data, BorderStationsService.updateStaff, getStaff);
		}
		
		
		// UPDATE calls
		function updateCommitteeMembers(committeeMembers) {
			var defered = $q.defer();
			vm.updateRelationship(committeeMembers, BorderStationsService.updateCommitteeMembers, vm.people.committeeMembers.data.length).then(function() {
				defered.resolve('Finished updating Committee Members');
			}, function(error) {
				defered.reject(error);
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
			
			vm.updateRelationship([details], BorderStationsService.updateDetails).then(function() {
				defered.resolve('Finished updating Details');
			}, function(error) {
				defered.reject(error);
			});
			return defered.promise;
		}
		
		function updateLocations(locations) {
			var defered = $q.defer();
			vm.updateRelationship(locations, BorderStationsService.updateLocations, vm.locations.length).then(function() {
				defered.resolve('Finished updating Locations');
			}, function(error) {
				defered.reject(error);
			});
			return defered.promise;
		}
		
		function updateRelationship(updateArray, updateApiFunction, numberOfNewValues) {
			return BorderStationsService.updateRelationship(updateArray, updateApiFunction, numberOfNewValues, vm.handleErrors);
		}
		
		function updateStaff(staff) {
			var defered = $q.defer();
			vm.updateRelationship(staff, BorderStationsService.updateStaff, vm.newStaff.length).then(function() {
				defered.resolve('Finished updating Staff');
			}, function(error) {
				defered.reject(error);
			});
			return defered.promise;
		}
		
		function updateStation() {
			vm.updateStatusText = 'Saving...';
			
			vm.errors = [];
			
			var promises = [];
			
			promises.push(createCommitteeMembers(vm.newCommitteeMembers));
			promises.push(createLocations(vm.newLocations));
			promises.push(createStaff(vm.newStaff));
			
			promises.push(updateDetails(vm.details));
			promises.push(updateCommitteeMembers(vm.people.committeeMembers.data));
			promises.push(updateLocations(vm.locations));
			promises.push(updateStaff(vm.people.staff.data));
			
			
			$q.all(promises).then(function() {
				getData();
				vm.updateStatusText = 'Saved';
				$timeout(function() {
					vm.updateStatusText = updateButtonText;
				}, 2000);
			}, function(error) {
				console.log(error);
				vm.updateStatusText = 'Error';
				$timeout(function() {
					vm.updateStatusText = updateButtonText;
				}, 4000);
			});
		}
	}
})();