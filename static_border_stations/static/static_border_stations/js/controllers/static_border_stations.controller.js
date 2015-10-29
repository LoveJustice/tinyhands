(function() {
	'use strict';
	
	angular.module('BorderStationsMod')
		.controller('BorderStationsCtrl', BorderStationsCtrl);
		
	BorderStationsCtrl.$inject = ['$q','$timeout','BorderStationsService'];
		
	function BorderStationsCtrl($q, $timeout, BorderStationsService) {
		var vm = this;
		
		var createCommitteeMembersDeferredMessage = 'Finished creating Committee Members';
		var createLocationsDeferredMessage = 'Finished creating Locations';
		var createStaffDeferredMessage = 'Finished creating Staff';
		var committeeMemTitle = 'Committee Members';
		var staffTitle = 'Staff';
		var updateButtonText = 'Update Station';
		
		vm.addLocation = addLocation;
		vm.addPerson = addPerson;
		vm.borderStationId = window.border_station_pk;
		vm.changeStationStatus = changeStationStatus;
		vm.createCommitteeMembers = createCommitteeMembers;
		vm.createLocations = createLocations;
		vm.createStaff = createStaff;
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
		vm.removeCommitteeMember = removeCommitteeMember;
		vm.removeLocation = removeLocation;
		vm.removePerson = removePerson;
		vm.removeRelationship = removeRelationship;
		vm.removeStaff = removeStaff;
		vm.updateCommitteeMembers = updateCommitteeMembers;
		vm.updateDetails = updateDetails;
		vm.updateLocations = updateLocations;
		vm.updateRelationship = updateRelationship;
		vm.updateStaff = updateStaff;
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
			return vm.createRelationship(members, BorderStationsService.createCommitteeMember, createCommitteeMembersDeferredMessage);
		}
		
		function createLocations(locations) {
			return vm.createRelationship(locations, BorderStationsService.createLocation, createLocationsDeferredMessage);
		}
		
		function createRelationship(createArray, createApiFunction, resolveMessage) {
			var deferred = $q.defer();
			BorderStationsService.createRelationship(createArray, createApiFunction, vm.handleErrors).then(function() {
				deferred.resolve(resolveMessage);
			}, function(error) {
				deferred.reject(error);
			});
			return deferred.promise;
		}
		
		function createStaff(staff) {
			return vm.createRelationship(staff, BorderStationsService.createStaff, createStaffDeferredMessage);
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
				persons.name == staffTitle ? vm.removeStaff(person) : vm.removeCommitteeMember(person);
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
			return vm.updateRelationship(committeeMembers, BorderStationsService.updateCommitteeMembers, vm.newCommitteeMembers.length, 'Finished updating Committee Members');
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
			
			return vm.updateRelationship([details], BorderStationsService.updateDetails, 0, 'Finished updating Details');
		}
		
		function updateLocations(locations) {
			return vm.updateRelationship(locations, BorderStationsService.updateLocations, vm.newLocations.length, 'Finished updating Locations');
		}
		
		function updateRelationship(updateArray, updateApiFunction, numberOfNewValues, resolveMessage) {
			var deferred = $q.defer();
			BorderStationsService.updateRelationship(updateArray, updateApiFunction, numberOfNewValues, vm.handleErrors).then(function() {
				deferred.resolve(resolveMessage);
			}, function(error) {
				deferred.reject(error);
			});
			return deferred.promise;
		}
		
		function updateStaff(staff) {
			return vm.updateRelationship(staff, BorderStationsService.updateStaff, vm.newStaff.length, 'Finished updating Staff');
		}
		
		function updateStation() {
			vm.updateStatusText = 'Saving...';
			
			vm.errors = [];
			
			var promises = [];
			
			promises.push(vm.createCommitteeMembers(vm.newCommitteeMembers));
			promises.push(vm.createLocations(vm.newLocations));
			promises.push(vm.createStaff(vm.newStaff));
			
			promises.push(vm.updateCommitteeMembers(vm.people.committeeMembers.data));
			promises.push(vm.updateDetails(vm.details));
			promises.push(vm.updateLocations(vm.locations));
			promises.push(vm.updateStaff(vm.people.staff.data));
			
			
			$q.all(promises).then(function() {
				vm.newCommitteeMembers = [];
				vm.newLocations = [];
				vm.newStaff = [];
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