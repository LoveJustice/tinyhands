(function() {
	'use strict';
	
	angular.module('BorderStationsMod')
		.controller('BorderStationsCtrl', BorderStationsCtrl);
		
	BorderStationsCtrl.$inject = ['BorderStationsService'];
		
	function BorderStationsCtrl(BorderStationsService) {
		var vm = this;
		
		vm.details = {};
		
		activate();
		
		function activate() {
			getBorderstation();
			getStaff();
			getCommitteeMembers();
			getLocations();
		}
		
		function getBorderstation() {
			BorderStationsService.getStation(0).then(function(data) {
				vm.details = data.data;
			});
		}
		
		function getStaff() {
			BorderStationsService.getStaff(0).then(function(data) {
				console.log(data);
				// vm.details = data.data;
			});
		}
		
		function getCommitteeMembers() {
			BorderStationsService.getCommitteeMembers(0).then(function(data) {
				console.log(data);
				// vm.details = data.data;
			});
		}
		
		function getLocations() {
			BorderStationsService.getLocations(0).then(function(data) {
				console.log(data);
				// vm.details = data.data;
			});
		}
	}
})();