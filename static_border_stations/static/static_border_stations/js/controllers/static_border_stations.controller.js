(function() {
	'use strict';
	
	angular.module('BorderStationsMod')
		.controller('BorderStationsCtrl', BorderStationsCtrl);
		
	BorderStationsCtrl.$inject = ['BorderStationsService'];
		
	function BorderStationsCtrl(BorderStationsService) {
		var vm = this;
		
		var staffTitle = 'Staff';
		var committeeMemTitle = 'Committee Members';
		
		vm.addLocation = addLocation;
		vm.addPerson = addPerson;
		vm.borderStationId = window.border_station_pk;
		vm.details = {};
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
		
		activate();
		
		function activate() {
			getDetails();
			getStaff();
			getCommitteeMembers();
			getLocations();
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
		
		function createCommitteeMembers(members) {
			createRelationship(members, BorderStationsService.createCommitteeMember, getCommitteeMembers);
		}
		
		function createLocations(locations) {
			createRelationship(locations, BorderStationsService.createLocation, getLocations);
		}
		
		function createStaff(staff) {
			createRelationship(staff, BorderStationsService.createStaff, getStaff);
		}
		
		function createRelationship(createArray, createApiFunction, getApiFunction) {
			createArray.forEach(function (anObject) {
				createApiFunction(anObject).then(function() {
					getApiFunction();
				});
			});
			createArray = []; // Empty the array after all of the create calls have been fired.
		}
		
		function getDetails() {
			BorderStationsService.getDetails(vm.borderStationId).then(function(response) {
				vm.details = response.data;
			});
		}
		
		function getCommitteeMembers() {
			BorderStationsService.getCommitteeMembers(vm.borderStationId).then(function(response) {
				vm.people.committeeMembers.data = response.data;
			});
		}
		
		function getLocations() {
			BorderStationsService.getLocations(vm.borderStationId).then(function(response) {
				vm.locations = response.data;
			});
		}
		
		function getStaff() {
			BorderStationsService.getStaff(vm.borderStationId).then(function(response) {
				vm.people.staff.data = response.data;
			});
		}
		
		function removeCommitteeMember(member) {
			removeRelation(member, vm.newCommitteeMembers, vm.people.committeeMembers.data, BorderStationsService.updateCommitteeMembers, getCommitteeMembers);
		}
		
		function removeLocation(location) {
			removeRelation(location, vm.newLocations, vm.locations, BorderStationsService.updateLocations, getLocations);
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
						getApiFunction();
					});
				}
			}
		}
		
		function removeStaff(staff) {
			removeRelation(staff, vm.newStaff, vm.people.staff.data, BorderStationsService.updateStaff, getStaff);
		}
		
		function updateCommitteeMembers(committeeMembers) {
			updateRelationship(committeeMembers, BorderStationsService.updateCommitteeMembers, getCommitteeMembers);
		}
		
		function updateDetails(details) {
			BorderStationsService.updateDetails(details.id, details);
		}
		
		function updateLocations(locations) {
			updateRelationship(locations, BorderStationsService.updateLocations, getLocations);
		}
		
		function updateStaff(staff) {
			updateRelationship(staff, BorderStationsService.updateStaff, getStaff);
		}
		
		function updateRelationship(updateArray, updateApiFunction, getApiFunction) {
			updateArray.forEach(function(anObject) {
				if (anObject.id) {
					updateApiFunction(anObject.id, anObject).then(function() {
						getApiFunction();
					});
				}
			});
		}
		
		function updateStation() {
			createCommitteeMembers(vm.newCommitteeMembers);
			createLocations(vm.newLocations);
			createStaff(vm.newStaff);
			
			updateDetails(vm.details);
			updateCommitteeMembers(vm.people.committeeMembers.data);
			updateLocations(vm.locations);
			updateStaff(vm.people.staff.data);
		}
	}
})();