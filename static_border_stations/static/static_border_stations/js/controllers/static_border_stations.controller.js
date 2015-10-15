(function() {
	'use strict';
	
	angular.module('BorderStationsMod')
		.controller('BorderStationsCtrl', BorderStationsCtrl);
		
	BorderStationsCtrl.$inject = ['$q','$timeout','BorderStationsService'];
		
	function BorderStationsCtrl($q, $timeout, BorderStationsService) {
		var vm = this;
		
		var defer = $q.defer();
		var committeeMemTitle = 'Committee Members';
		var staffTitle = 'Staff';
		var updateButtonText = 'Update Station';
		
		vm.addLocation = addLocation;
		vm.addPerson = addPerson;
		vm.borderStationId = window.border_station_pk;
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
		
		
		// CREATE calls
		function createCommitteeMembers(members) {
			createRelationship(members, BorderStationsService.createCommitteeMember, BorderStationsService.getCommitteeMembers);
		}
		
		function createLocations(locations) {
			createRelationship(locations, BorderStationsService.createLocation, BorderStationsService.getLocations);
		}
		
		function createStaff(staff) {
			createRelationship(staff, BorderStationsService.createStaff, BorderStationsService.getStaff);
		}
		
		function createRelationship(createArray, createApiFunction, getApiFunction) {
			createArray.forEach(function (anObject) {
				createApiFunction(anObject).then(function() {
					getApiFunction(vm.borderStationId).then(function() {}, handleErrors);
					defer.resolve();
				}, handleErrors);
			});
			createArray = []; // Empty the array after all of the create calls have been fired.
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
					vm.people.committeeMembers.data = response.data;
				}, handleErrors);
			}
		}
		
		function getLocations() {
			if (vm.borderStationId) {
				BorderStationsService.getLocations(vm.borderStationId).then(function(response) {
					vm.locations = response.data;
				}, handleErrors);
			}
		}
		
		function getStaff() {
			if (vm.borderStationId) {
				BorderStationsService.getStaff(vm.borderStationId).then(function(response) {
					vm.people.staff.data = response.data;
				}, handleErrors);
			}
		}
		
		
		// REMOVE calls
		function removeCommitteeMember(member) {
			removeRelation(member, vm.newCommitteeMembers, vm.people.committeeMembers.data, BorderStationsService.updateCommitteeMembers, BorderStationsService.getCommitteeMembers);
		}
		
		function removeLocation(location) {
			removeRelation(location, vm.newLocations, vm.locations, BorderStationsService.updateLocations, BorderStationsService.getLocations);
		}
		
		function removePerson(persons, person) {
			persons.name == staffTitle ? removeStaff(person) : removeCommitteeMember(person);
		}
		
		function removeRelation(value, newArray, currentArray, updateApiFunction, getApiFunction) {
			var idx = newArray.indexOf(value);
			if (idx >= 0) { // If relation was just created and isnt (shouldnt be) in the db
				newArray.splice(idx, 1);
				
				idx = currentArray.indexOf(value);
				currentArray.splice(idx, 1);
			} else { // If exists in db
				value.border_station = null;
				if (value.id) {
					updateApiFunction(value.id, value).then(function() {
						getApiFunction(vm.borderStationId).then(function() {}, handleErrors);
						defer.resolve();
					}, handleErrors);
				}
			}
		}
		
		function removeStaff(staff) {
			removeRelation(staff, vm.newStaff, vm.people.staff.data, BorderStationsService.updateStaff, BorderStationsService.getStaff);
		}
		
		
		// UPDATE calls
		function updateCommitteeMembers(committeeMembers) {
			updateRelationship(committeeMembers, BorderStationsService.updateCommitteeMembers, BorderStationsService.getCommitteeMembers);
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
			
			updateRelationship([details], BorderStationsService.updateDetails, BorderStationsService.getDetails);
		}
		
		function updateLocations(locations) {
			updateRelationship(locations, BorderStationsService.updateLocations, BorderStationsService.getLocations);
		}
		
		function updateStaff(staff) {
			updateRelationship(staff, BorderStationsService.updateStaff, BorderStationsService.getStaff);
		}
		
		function updateRelationship(updateArray, updateApiFunction, getApiFunction) {
			updateArray.forEach(function(anObject) {
				if (anObject.id) {
					updateApiFunction(anObject.id, anObject).then(function() {
						getApiFunction(vm.borderStationId).then(function() {}, handleErrors);
						defer.resolve();
					}, handleErrors);
				}
			});
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