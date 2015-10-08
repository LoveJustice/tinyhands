(function() {
	'use strict';
	
	angular.module('BorderStationsMod')
		.controller('BorderStationsCtrl', BorderStationsCtrl);
		
	BorderStationsCtrl.$inject = ['BorderStationsService'];
		
	function BorderStationsCtrl(BorderStationsService) {
		var vm = this;
		
		vm.details = {};
		vm.locations = [];
		vm.people = {
			staff: {
				name: 'Staff'
			},
			committeeMembers: {
				name: 'Committee Members'
			}
		};
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
			BorderStationsService.getDetails(0).then(function(response) {
				vm.details = response.data;
			});
		}
		
		function getCommitteeMembers() {
			BorderStationsService.getCommitteeMembers(0).then(function(response) {
				vm.people.committeeMembers.data = response.data;
			});
		}
		
		function getLocations() {
			BorderStationsService.getLocations(0).then(function(response) {
				vm.locations = response.data;
			});
		}
		
		function getStaff() {
			BorderStationsService.getStaff(0).then(function(response) {
				vm.people.staff.data = response.data;
			});
		}
		
		function removePerson(person) {
			person.border_station = null;
			
		}
		
		function updateStation() {
			updateDetails(vm.details);
			updateCommitteeMembers(vm.people.committeeMembers.data);
			updateLocations(vm.locations);
			updateStaff(vm.people.staff.data);
		}
		
		function updateDetails(details) {
			BorderStationsService.updateDetails(vm.details.id, details);
		}
		
		function updateCommitteeMembers(committeeMembers) {
			committeeMembers.forEach(function(member) {
				BorderStationsService.updateCommitteeMembers(member.id, member);
			});
		}
		
		function updateLocations(locations) {
			locations.forEach(function(location) {
				BorderStationsService.updateLocations(location.id, location);
			});
		}
		
		function updateStaff(staff) {
			vm.people.staff.data.forEach(function(staff) {
				BorderStationsService.updateStaff(staff.id, staff);
			});
		}
	}
})();