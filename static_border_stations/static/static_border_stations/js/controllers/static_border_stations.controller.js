(function() {
	'use strict';
	
	angular.module('BorderStationsMod')
		.controller('BorderStationsCtrl', BorderStationsCtrl);
		
	BorderStationsCtrl.$inject = ['BorderStationsService'];
		
	function BorderStationsCtrl(BorderStationsService) {
		var vm = this;
		
		var staffTitle = 'Staff';
		
		vm.borderStationId = window.border_station_pk
		vm.details = {};
		vm.locations = [];
		vm.people = {
			staff: {
				name: staffTitle
			},
			committeeMembers: {
				name: 'Committee Members'
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
			console.log(vm.people);
		}
		
		function getDetails() {
			BorderStationsService.getDetails(vm.borderStationId).then(function(response) {
				vm.details = response.data;
			});
		}
		
		function getCommitteeMembers() {
			BorderStationsService.getCommitteeMembers(vm.borderStationId).then(function(response) {
				vm.people.committeeMembers.data = response.data;
				console.log('Got the peeps');
			});
		}
		
		function getLocations() {
			BorderStationsService.getLocations(vm.borderStationId).then(function(response) {
				vm.locations = response.data;
				console.log(response.data);
			});
		}
		
		function getStaff() {
			BorderStationsService.getStaff(vm.borderStationId).then(function(response) {
				vm.people.staff.data = response.data;
			});
		}
		
		function removeCommitteeMember(member) {
			member.border_station = null;
			BorderStationsService.updateCommitteeMembers(member.id, member);
			getCommitteeMembers();
		}
		
		function removeLocation(location) {
			location.border_station = null;
			updateLocations([location]);
			getLocations();
		}
		
		function removePerson(persons, person) {
			persons.name == staffTitle ? removeStaff(person) : removeCommitteeMember(person);
		}
		
		function removeStaff(staff) {
			staff.border_station = null;
			updateStaff([staff]);
			getStaff();
		}
		
		function updateCommitteeMembers(committeeMembers) {
			committeeMembers.forEach(function(member) {
				BorderStationsService.updateCommitteeMembers(member.id, member);
			});
		}
		
		function updateDetails(details) {
			BorderStationsService.updateDetails(vm.details.id, details);
		}
		
		function updateLocations(locations) {
			locations.forEach(function(location) {
				BorderStationsService.updateLocations(location.id, location);
			});
		}
		
		function updateStaff(staff) {
			staff.data.forEach(function(aStaff) {
				BorderStationsService.updateStaff(aStaff.id, aStaff);
			});
		}
		
		function updateStation() {
			updateDetails(vm.details);
			updateCommitteeMembers(vm.people.committeeMembers.data);
			updateLocations(vm.locations);
			updateStaff(vm.people.staff.data);
		}
	}
})();