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
		vm.loading = false;
		vm.locations = [];
		vm.newCommitteeMembers = [];
		vm.newLocations = [];
		vm.newStaff = [];
		vm.people = {
			staff: {
				data: [],
				name: staffTitle
			},
			committeeMembers: {
				data: [],
				name: committeeMemTitle
			}
		};
		vm.removeCommitteeMember = removeCommitteeMember;
		vm.removeLocation = removeLocation;
		vm.removePerson = removePerson;
		vm.removeRelationship = removeRelationship;
		vm.removeStaff = removeStaff;
		vm.removeToCommitteeMembers = [];
		vm.removeToLocations = [];
		vm.removeToStaff = [];
		vm.updateCommitteeMembers = updateCommitteeMembers;
		vm.updateDetails = updateDetails;
		vm.updateLocations = updateLocations;
		vm.updateRelationship = updateRelationship;
		vm.updateStaff = updateStaff;
		vm.updateStation = updateStation;
		vm.updateStatusText = updateButtonText;
		
		activate();
		
		function activate() {
			getBorderStationData();
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
			return BorderStationsService.createRelationship(createArray, createApiFunction, vm.handleErrors);
		}
		
		function createStaff(staff) {
			return vm.createRelationship(staff, BorderStationsService.createStaff, createStaffDeferredMessage);
		}
		
		
		// Date Formatting
		function formatDate (dateToFormat) { // Formats date to yyyy[-mm[-dd]]
			var dateEstablished = new Date(dateToFormat);
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
			return dateString;
		}
		
		
		// GET calls
		function getBorderStationData() {
			vm.loading = true;
			
			var promises = [];
			
			promises.push(getCommitteeMembers());
			promises.push(getDetails());
			promises.push(getLocations());
			promises.push(getStaff());
			
			$q.all(promises).then(function(data) {
				for (var i = 0; i < data.length; i++) {
					switch (i) { // Data returns in the order of which the promises were placed in the array
						case 0:
							vm.people.committeeMembers.data = data[i];
							break;
						case 1:
							vm.details = data[i];
							break;
						case 2:
							vm.locations = data[i];
							break;
						case 3:
							vm.people.staff.data = data[i];
							break;
						default:
							break;
					}
				}
				vm.loading = false;
			});
		}
		
		function getBorderStationDataHelper(getApiCall) {
			return BorderStationsService.getBorderStationDataHelper(getApiCall, vm.borderStationId, vm.handleErrors);
		}
		
		function getCommitteeMembers() {
			return getBorderStationDataHelper(BorderStationsService.getCommitteeMembers);
		}
		
		function getDetails() {
			return getBorderStationDataHelper(BorderStationsService.getDetails);
		}
		
		function getLocations() {
			return getBorderStationDataHelper(BorderStationsService.getLocations);
		}
		
		function getStaff() {
			return getBorderStationDataHelper(BorderStationsService.getStaff);
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
			vm.removeRelationship(member, vm.newCommitteeMembers, vm.people.committeeMembers.data, vm.removeToCommitteeMembers);
		}
		
		function removeLocation(location) {
			if (location.removeConfirmed) {
				vm.removeRelationship(location, vm.newLocations, vm.locations, vm.removeToLocations);
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
		
		function removeRelationship(value, newArray, currentArray, removeArray) {
			BorderStationsService.removeRelationship(value, newArray, currentArray, removeArray);
		}
		
		function removeStaff(staff) {
			vm.removeRelationship(staff, vm.newStaff, vm.people.staff.data, vm.removeToStaff);
		}
		
		
		// UPDATE calls
		function updateCommitteeMembers(committeeMembers) {
			return vm.updateRelationship(committeeMembers, BorderStationsService.updateCommitteeMembers, vm.newCommitteeMembers.length, 'Finished updating Committee Members');
		}
		
		function updateDetails(details) {
			details.date_established = formatDate(details.date_established);
			
			return vm.updateRelationship([details], BorderStationsService.updateDetails, 0, 'Finished updating Details');
		}
		
		function updateLocations(locations) {
			return vm.updateRelationship(locations, BorderStationsService.updateLocations, vm.newLocations.length, 'Finished updating Locations');
		}
		
		function updateRelationship(updateArray, updateApiFunction, numberOfNewValues, resolveMessage) {
			return BorderStationsService.updateRelationship(updateArray, updateApiFunction, numberOfNewValues, vm.handleErrors);
		}
		
		function updateStaff(staff) {
			return vm.updateRelationship(staff, BorderStationsService.updateStaff, vm.newStaff.length, 'Finished updating Staff');
		}
		
		function updateStation() {
			vm.updateStatusText = 'Saving...';
			
			vm.errors = [];
			
			var promises = [];
			
			// Create Calls
			promises.push(vm.createCommitteeMembers(vm.newCommitteeMembers));
			promises.push(vm.createLocations(vm.newLocations));
			promises.push(vm.createStaff(vm.newStaff));
			
			// Update Calls
			promises.push(vm.updateCommitteeMembers(vm.people.committeeMembers.data));
			promises.push(vm.updateDetails(vm.details));
			promises.push(vm.updateLocations(vm.locations));
			promises.push(vm.updateStaff(vm.people.staff.data));
			
			// Remove Calls
			promises.push(vm.updateCommitteeMembers(vm.removeToCommitteeMembers));
			promises.push(vm.updateLocations(vm.removeToLocations));
			promises.push(vm.updateStaff(vm.removeToStaff));
			
			
			$q.all(promises).then(function() {
				vm.newCommitteeMembers = [];
				vm.newLocations = [];
				vm.newStaff = [];
				getBorderStationData();
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